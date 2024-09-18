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

// 카메라를 전역으로 열어 유지
cv::VideoCapture cap;

// Capture frame using OpenCV
cv::Mat capture_frame() {
    if (!cap.isOpened()) {
        std::cerr << "Error: Camera is not open!" << std::endl;
        return cv::Mat();
    }

    cv::Mat frame;
    cap >> frame; // Capture a frame
    return frame;
}

// Function to send a frame over the WebSocket connection
void send_frame(websocket::stream<tcp::socket>& ws, const cv::Mat& frame) {
    std::vector<uchar> buf;
    std::vector<int> params = { cv::IMWRITE_JPEG_QUALITY, 80 };
    cv::imencode(".jpg", frame, buf, params);

    // Send the frame data as a binary message
    ws.write(net::buffer(buf));
}

// Function to handle WebSocket sessions asynchronously
void handle_session(tcp::socket socket) {
    try {
        websocket::stream<tcp::socket> ws(std::move(socket));

        // Accept the WebSocket handshake
        ws.accept();

        while (true) {
            cv::Mat frame = capture_frame();
            if (!frame.empty()) {
                send_frame(ws, frame);
            }

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
        // Initialize the camera (0번 카메라 열기)
        cap.open(0);
        if (!cap.isOpened()) {
            std::cerr << "Error: Cannot open camera!" << std::endl;
            return -1;
        }

        // Initialize the Boost Asio context
        net::io_context ioc;

        // Define the endpoint (IP address and port)
        tcp::endpoint endpoint(tcp::v4(), 10001);

        std::cout << "WebSocket server listening on port 10001..." << std::endl;

        // Run the server
        run_server(ioc, endpoint);
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}
