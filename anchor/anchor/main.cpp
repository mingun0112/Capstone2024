#include <boost/beast/core.hpp>
#include <boost/beast/websocket.hpp>
#include <boost/asio.hpp>
#include <opencv2/opencv.hpp>
#include <iostream>
#include <thread>
#include <vector>

namespace beast = boost::beast;
namespace websocket = beast::websocket;
namespace net = boost::asio;
using tcp = boost::asio::ip::tcp;

// Number of cameras to handle
const int NUM_CAMERAS = 4;

// Capture frame using OpenCV
cv::Mat capture_frame(int camera_index) {
    /*std::string device = "/dev/video" + std::to_string(camera_index);
    cv::VideoCapture cap(device);*/
    cv::VideoCapture cap(0);

    if (!cap.isOpened()) {
        std::cerr << "Error opening camera: " << camera_index << std::endl;
        return cv::Mat();
    }

    cv::Mat frame;
    cap >> frame; // Capture a frame
    return frame;
}

// Function to send a frame over the WebSocket connection
void send_frame(websocket::stream<tcp::socket>& ws, int camera_index, const cv::Mat& frame) {
    std::vector<uchar> buf;
    std::vector<int> params = { cv::IMWRITE_JPEG_QUALITY, 80 };
    cv::imencode(".jpg", frame, buf, params);

    // Prepend camera index
    std::vector<unsigned char> final_buf;
    final_buf.push_back(static_cast<unsigned char>(camera_index));
    final_buf.insert(final_buf.end(), buf.begin(), buf.end());

    // Send the frame data as a binary message
    ws.write(net::buffer(final_buf));
}

// Function to handle WebSocket sessions asynchronously
void handle_session(tcp::socket socket) {
    try {
        websocket::stream<tcp::socket> ws(std::move(socket));

        // Accept the WebSocket handshake
        ws.accept();

        // WebSocket will continuously send frames from all cameras
        while (true) {
            for (int i = 0; i < NUM_CAMERAS; ++i) {
                cv::Mat frame = capture_frame(i);
                if (!frame.empty()) {
                    send_frame(ws, i, frame);
                }
            }
            // Sleep briefly between frame captures to avoid overloading
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }
    catch (const beast::system_error& se) {
        std::cerr << "Error: " << se.what() << std::endl;
    }
}

// Main server function to accept incoming WebSocket connections
void run_server(net::io_context& ioc, tcp::endpoint endpoint) {
    tcp::acceptor acceptor(ioc, endpoint);

    while (true) {
        tcp::socket socket(ioc);

        // Blocking wait for a connection
        acceptor.accept(socket);

        // Start a new thread for each client to handle sessions concurrently
        std::thread(&handle_session, std::move(socket)).detach();
    }
}

int main() {
    try {
        // Initialize the Boost Asio context
        net::io_context ioc;

        // Define the endpoint (IP address and port)
        tcp::endpoint endpoint(tcp::v4(), 10000);

        std::cout << "WebSocket server listening on port 10000..." << std::endl;

        // Run the server
        run_server(ioc, endpoint);
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
