x_dim = 100
y_dim = 100

delta_x = 10
delta_y = 10

x_p = 50
y_p = 50

points_x = list(range(x_p, x_dim + x_p + delta_x, delta_x))
points_y = list(range(y_p, y_dim + y_p + delta_y, delta_y))

points = []
for j in range(len(points_y)):
  for i in range(len(points_x)):
    points.append((points_x[i], points_y[j]))

archivo = open("gcode.gcode", "w")

for point in points:
  archivo.write('''G0 X{} Y{};\n'''.format(point[0], point[1]))

archivo.write("G0 X0 Y0;\n")