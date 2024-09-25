import numpy as np
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # 3D 시각화를 위한 라이브러리

# 3D 그리드 설정 (10x10x10 크기의 빈 그리드 생성)
grid = np.zeros((10, 10, 10))
grid[4:6, 4:6, 4:6] = 1  # 장애물 추가 (4,4,4)에서 (6,6,6)까지

# 랜드마크 설정 (3D 공간 내 랜드마크 위치)
landmarks = [[0, 0, 0], [9, 9, 9], [0, 9, 0], [0, 0, 9]]  # 랜드마크 위치
landmark_noises = [0.5, 0.3, 0.7, 0.4]  # 각 랜드마크에 대한 센서 노이즈 크기 설정
sensor_ranges = [7, 7, 7, 6]  # 각 랜드마크의 센서 범위 설정
for landmark in landmarks:
    grid[landmark[0], landmark[1], landmark[2]] = 1  # 랜드마크 위치에 장애물 표시

class Particle:
    def __init__(self):
        # 파티클의 초기 위치를 랜덤하게 설정
        while True:
            self.x = random.choice(range(grid.shape[0]))
            self.y = random.choice(range(grid.shape[1]))
            self.z = random.choice(range(grid.shape[2]))
            if grid[self.x, self.y, self.z] == 0:  # 유효한 위치인지 확인
                break

    def move(self):
        # 파티클이 이동할 수 있는 방향 설정 (6방향)
        directions = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
        dx, dy, dz = directions[random.randint(0, 5)]  # 랜덤한 방향 선택
        # 이동 후 유효한 위치인지 확인
        if (0 <= self.x + dx < grid.shape[0]) and (0 <= self.y + dy < grid.shape[1]) and (0 <= self.z + dz < grid.shape[2]) and grid[self.x + dx, self.y + dy, self.z + dz] == 0:
            self.x += dx  # x 좌표 이동
            self.y += dy  # y 좌표 이동
            self.z += dz  # z 좌표 이동
        return self

    def measure_prob(self, Z, sense_noise, sensor_range):
        # 랜드마크와의 거리 측정 및 확률 계산
        distance = np.sqrt((self.x - Z[0]) ** 2 + (self.y - Z[1]) ** 2 + (self.z - Z[2]) ** 2)  # 센서로부터의 거리

        # 센서 범위 내에서만 측정 가능
        if distance <= sensor_range:
            # 랜드마크에 따라 독립적으로 노이즈 추가
            sensor_value = distance + np.random.normal(0, sense_noise)  # 측정 거리 + 노이즈
            measured_distance = sensor_value  # 측정된 거리

            # 확률 계산
            return np.exp(-((distance - measured_distance) ** 2) / (sense_noise ** 2) / 2.0) / np.sqrt(2.0 * np.pi * (sense_noise ** 2))
        else:
            return 0  # 센서 범위를 초과한 경우 확률은 0

# 파티클 생성 (1000개)
particles = [Particle() for _ in range(1000)]

for t in range(30):  # 14번의 시간 단계 반복
    particles = [p.move() for p in particles]  # 모든 파티클 이동

    weights = []  # 파티클의 가중치를 저장할 리스트
    for p in particles:
        total_weight = 0
        for idx, landmark in enumerate(landmarks):
            Z = np.array(landmark)  # 각 랜드마크 사용
            weight = p.measure_prob(Z, landmark_noises[idx], sensor_ranges[idx])  # 센서 범위 추가
            total_weight += weight  # 가중치 누적
        weights.append(total_weight)  # 총 가중치 추가

    weights = np.array(weights, dtype=np.float64)  # 가중치를 NumPy 배열로 변환
    total_weight = np.sum(weights)  # 총 가중치 계산
    if total_weight == 0:
        weights = np.ones_like(weights) / len(particles)  # 가중치가 0일 경우 균등 분포
    else:
        weights /= total_weight  # 가중치 정규화
    particles = random.choices(particles, weights=weights, k=len(particles))  # 가중치에 따라 파티클 재샘플링
    estimate = np.average([[p.x, p.y, p.z] for p in particles if grid[p.x, p.y, p.z] == 0], axis=0, weights=weights)  # 파티클 평균 위치 추정

    # 3D 시각화
    print(estimate) #예상되는 로봇의 위치 ( t값이라고 생각하시면 될 것 같습니다)
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')  # 3D 축 설정
    ax.voxels(grid, facecolors='blue', edgecolor='k')  # 그리드 시각화
    ax.scatter([p.x + random.gauss(0, 0.3) for p in particles], 
               [p.y + random.gauss(0, 0.3) for p in particles], 
               [p.z + random.gauss(0, 0.3) for p in particles], color='green')  # 파티클 위치 시각화
    for landmark in landmarks:
        ax.scatter(*landmark, color='red', s=100)  # 랜드마크 시각화
    ax.scatter(*estimate, color='red', marker='+', s=200)  # 추정 위치 시각화 (더 큰 마커)
    ax.text(*estimate, f'Estimate: {estimate}', color='black')  # 추정 위치 좌표 표시
    ax.set_title(f'Time step: {t+1}')  # 제목 설정
    plt.show()
