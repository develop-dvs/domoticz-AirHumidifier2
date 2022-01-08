import numpy as np

# Данные с датчика глубины
level = 50

# Пограничные текущие значения с датчика
max = 83
min = 32

# Исходные значения
maxReal = 100  # Да, тут может быть и 120 (depth) и даже 125. Китайцы они такие.
minReal = 0

# Решаем систему уравнений
m_list = [[max, 1], [min, 1]]
r_list = [maxReal, minReal]
A = np.array(m_list)
B = np.array(r_list)
X = np.linalg.inv(A).dot(B)

print(X)
# Решаем уравнение
result = X[0]*level+X[1]
print(result)

