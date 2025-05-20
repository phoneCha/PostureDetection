import math as m

class AngleCalculator:
    @staticmethod
    def find_angle(x1, y1, x2, y2, x3, y3):
        try:
            angle = m.degrees(m.atan2(y3 - y2, x3 - x2) - m.atan2(y1 - y2, x1 - x2))
            angle = abs(angle)
            if angle > 180:
                angle = 360 - angle
            return angle
        except ZeroDivisionError:
            return 0

    @staticmethod
    def get_angle_range(angle):
        start = (int(angle) // 10) * 10
        end = start + 10
        return f"{start}-{end}"
