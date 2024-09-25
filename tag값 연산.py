import numpy as np
import math

def calculate_position(d1, d2, d3):
    # 사용자 정의 공식으로 점 P의 좌표 계산
    try:
        # x_P 계산 (수식의 수정 필요)
        x_value = -((d3**2 - d2**2 + 9) / (6)**2) - ((d1**2 - d3**2 + 6.25/52)**2) + d1**2
        
        # 음수 체크
        if x_value < 0:
            raise ValueError("Calculated value for x_P is negative, cannot compute square root.")

        y_P = (d3**2 - d2**2 + 9) / 5
        z_P = (d1**2 - d3**2 + 6.25) / 5
        x_P = math.sqrt(4- y_P**2- z_P**2)
        return np.array([x_P, y_P, z_P])
    except ValueError as e:
        print(e)
        return None

# 꼭지점 좌표 (예: 왼쪽 평면 꼭지점)
vertex1 = [0, 0, 0]
vertex2 = [0, 3, 2.5]
vertex3 = [0, 0, 2.5]

# 각 꼭지점으로부터의 거리 (예: 임의의 거리)
distance1 = float(input("Vertex 1 to P distance (d1): "))
distance2 = float(input("Vertex 2 to P distance (d2): "))
distance3 = float(input("Vertex 3 to P distance (d3): "))

# 점 P의 위치 계산
point_P = calculate_position(distance1, distance2, distance3)

# 결과 출력
if point_P is not None:
    print(f"The estimated position of point P is: {point_P}")
