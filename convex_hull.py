# this is 4-5 seconds slower on 1000000 points than Ryan's desktop...  Why?


from PyQt5.QtCore import QLineF, QPointF, QThread, pyqtSignal
import time
import math
from itertools import cycle



class ConvexHullSolverThread(QThread):
    listOfLinesToDraw = []

    def __init__(self, unsorted_points, demo):
        self.points = unsorted_points
        self.pause = demo
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    # These two signals are used for interacting with the GUI.
    show_hull = pyqtSignal(list, tuple)
    display_text = pyqtSignal(str)

    # Some additional thread signals you can implement and use for debugging,
    # if you like
    show_tangent = pyqtSignal(list, tuple)
    erase_hull = pyqtSignal(list)
    erase_tangent = pyqtSignal(list)

    def set_points(self, unsorted_points, demo):
        self.points = unsorted_points
        self.demo = demo

    def run(self):
        assert (type(self.points) == list and type(self.points[0]) == QPointF)

        n = len(self.points)
        print('Computing Hull for set of {} points'.format(n))

        t1 = time.time()

        # SORT THE POINTS BY INCREASING X-VALUE AND CLOCKWISE
        self.points.sort(key=lambda x: x.x())



        t2 = time.time()
        print('Time Elapsed (Sorting): {:3.3f} sec'.format(t2 - t1))

        t3 = time.time()

        # COMPUTE THE CONVEX HULL USING DIVIDE AND CONQUER
        solvedHull = self.divideInTwoRecursively(self.points)


        t4 = time.time()

        USE_DUMMY = False
        if USE_DUMMY:
            # This is a dummy polygon of the first 3 unsorted points
            polygon = [QLineF(self.points[i], self.points[(i + 1) % 3]) for i in range(3)]

            # When passing lines to the display, pass a list of QLineF objects.
            # Each QLineF object can be created with two QPointF objects
            # corresponding to the endpoints
            assert (type(polygon) == list and type(polygon[0]) == QLineF)

            # Send a signal to the GUI thread with the hull and its color
            self.show_hull.emit(polygon, (0, 255, 0))

        else:
            # PASS THE CONVEX HULL LINES BACK TO THE GUI FOR DISPLAY
            # DELETE 'PASS' AND REPLACE WITH THE 'ASSERT' AND 'SHOW_HULL' LINES

            polygon = [QLineF(solvedHull[i], solvedHull[(i + 1) % len(solvedHull)]) for i in range(len(solvedHull))]

            assert (type(polygon) == list and type(polygon[0]) == QLineF)

            # Send a signal to the GUI thread with the hull and its color
            # self.show_hull.emit(polygon, (255, 0, 0))

        # Send a signal to the GUI thread with the time used to compute the
        # hull
        self.display_text.emit('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))
        print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    # Recursively divide array in two
    def divideInTwoRecursively(self, points):
        # Base case for once the array of points has been divided to contain 3 points or less
        # Time complexity o(1) space comp: nothing
        if len(points) < 4:
            return points

        # Time comp: O(1) space comp: O(n-1)
        mid = len(points) // 2
        pointsL = self.divideInTwoRecursively(points[:mid])
        pointsR = self.divideInTwoRecursively(points[mid:])


        # Sort both arrays clockwise
        # Time comp: O(n) space comp: O(n)
        pointsL.sort(key=lambda point: math.atan2(point.y(), point.x()))
        pointsR.sort(key=lambda point: math.atan2(point.y(), point.x()))


        # SOLVE FOR TOP TANGENT LINE
        # Find angle of line between last point in pointsL and first point in pointsR
        # When traversing through pointsR, you want to find the line with SMALLEST ANGLE
        # When traversing through pointsL, you want to find the line with LARGEST ANGLE

        # Calculate the point in pointsL that has the greatest x value
        # time comp: O(n) space comp: O(n)
        highestLeftPoint = pointsL[0]
        for p in pointsL:
            if p.x() > highestLeftPoint.x():
                highestLeftPoint = p

        greatestXinPointsL = highestLeftPoint

        # Calculate the point in pointsR that has the smallest x value
        # Time comp: O(n) space comp: O(n)
        highestRightPoint = pointsR[0]
        for p in pointsR:
            if p.x() < highestRightPoint.x():
                highestRightPoint = p

        smallestXinPointsR = highestRightPoint

        # time comp: O(1) space comp: O(n-1)
        slope = self.findSlope(highestLeftPoint, highestRightPoint)

        # Continue looping until the top tangent stops sliding up
        # time comp: O(k+n) space comp: O(n)
        slopeWasChanged = True
        while slopeWasChanged:
            slopeWasChanged = False

            # Iterate through the right list until you find the point with the smallest angle
            for pointInRightArray in pointsR:
                tempSlope = self.findSlope(highestLeftPoint, pointInRightArray)
                if tempSlope > slope:
                    slope = tempSlope
                    highestRightPoint = pointInRightArray
                    slopeWasChanged = True

            # Iterate through the left list until you find the point with the greatest angle
            for pointInLeftArray in pointsL:
                tempSlope = self.findSlope(pointInLeftArray, highestRightPoint)
                if tempSlope < slope:
                    slope = tempSlope
                    highestLeftPoint = pointInLeftArray
                    slopeWasChanged = True

        # Draw the top tangent
        # time comp: O(n) space comp: O(n)
        # topTangent = QLineF(highestLeftPoint, highestRightPoint)
        # polygon = [topTangent]
        # assert (type(polygon) == list and type(polygon[0]) == QLineF)
        # self.show_hull.emit(polygon, (0, 255, 0))

        # SOLVE FOR BOTTOM TANGENT LINE
        # Find angle of line between last point in pointsL and first point in pointsR
        # When traversing through pointsR, you want to find the line with LARGEST ANGLE
        # When traversing through pointsL, you want to find the line with SMALLEST ANGLE

        # Variables needed to calculate the bottom tangent
        # time comp: O(1) space comp: O(n)
        lowestLeftPoint = greatestXinPointsL
        lowestRightPoint = smallestXinPointsR

        # time comp: O(1) space comp = O(n-1)
        slope = self.findSlope(lowestLeftPoint, lowestRightPoint)

        # Continue looping until the bottom tangent stops sliding down
        # time comp: O(k+n) space comp: O(n)
        slopeWasChanged = True
        while slopeWasChanged:
            slopeWasChanged = False

            # Iterate through the right list until you find the point with the greatest angle
            for pointInRightArray in pointsR:
                tempSlope = self.findSlope(lowestLeftPoint, pointInRightArray)
                if tempSlope < slope:
                    slope = tempSlope
                    lowestRightPoint = pointInRightArray
                    slopeWasChanged = True

            # Iterate through the left list until you find the point with the smallest angle
            for pointInLeftArray in pointsL:
                tempSlope = self.findSlope(pointInLeftArray, lowestRightPoint)
                if tempSlope > slope:
                    slope = tempSlope
                    lowestLeftPoint = pointInLeftArray
                    slopeWasChanged = True

        # Draw the bottom tangent
        # time comp: O(n) space comp: O(n)
        # bottomTangent = QLineF(lowestLeftPoint, lowestRightPoint)
        # polygon = [bottomTangent]
        # assert (type(polygon) == list and type(polygon[0]) == QLineF)
        # self.show_hull.emit(polygon, (0, 255, 255))

        # COMBINE THE ARRAYS AND TAKE OUT THE POINTS THAT AREN'T USED ANYMORE
        # Take out the corresponding points in pointsR that shouldn't be there
        indxToStartIterCCW = pointsR.index(highestRightPoint)
        indxToEndIterCCW = pointsR.index(lowestRightPoint)

        #for i in (i % len(pointsR) for i in range((indxToStartIterCCW + 1) % len(pointsR), indxToEndIterCCW)):
        #    pointsR[i] = ''
        #pointsR = list(filter(None, pointsR))

        # Take out the points to the right of pointsL upper and lower tangent points
        indxToStartIterCCW = pointsL.index(lowestLeftPoint)
        indxToEndIterCCW = pointsL.index(lowestLeftPoint)
        #for i in (i % len(pointsL) for i in range((indxToStartIterCCW + 1) % len(pointsL), indxToEndIterCCW)):
        #    pointsL[i] = ''
        #pointsL = list(filter(None, pointsL))

        # time comp: O(1) space comp: O(n+n)
        mergedHulls = pointsL + pointsR
        mergedHulls.sort(key=lambda point: math.atan2(point.y(), point.x()))

        return mergedHulls

    def findSlope(self, point1, point2):
        # time comp: O(1) space comp: O(n-1)
        return (point2.y() - point1.y()) / (point2.x() - point1.x())
