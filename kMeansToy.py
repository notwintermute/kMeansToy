import pygame
import math
import random

pygame.init()
# initializing the font
font = pygame.font.SysFont('calibri', 20)

# pi for later
pi = math.pi

# display resolution, right side is used for UI
squareRes = 600
UI = 402
resX = squareRes # setting the x and y to the same
resY = squareRes # value to get a square display

radius = 1  # radius of each dot
rnge = 1000  # range that the data takes (sharpness basically)
dSize = 5000  # number of dots
dType = 1 # type of data, 0 for clusters 1 for true random
oSize = dSize  # this is necessary if you clear the data and then want to generate new random data
data = []  # this is where the data (position of each point) are stored
centroids = []  # this is where the positions of the centroids are stored
noK = 1  # number of centroids
centDist = []  # this is where the distance of each point to each centroid is stored
for i in range(dSize):
    centDist.append([])

centBel = []  # this is where the centroid closest to a point is stored
familySize = []  # this is where the number of points belonging to a centroid is stored
for i in range(noK):
    familySize.append(0)

colors = []  # this is where colors are stored
minB = 80  # minimum brightness for colors
trails = True  # whether you display a trail between every update
centHist = []  # keeps track of the history of the centroids for trails
for x in range(noK):
    centHist.append([])

steps = 0  # number of steps
stepsT = 0  # number of steps in this trail
drawMode = 0  # mouse mode
Rad = 15  # brush radius
brushDen = 5  # brush density
drawing = False  # is left mouse button held while in draw mode
erasing = False  # is right mouse button held while in draw mode
mouseDist = []  # distance of centroids to mouse


# randomly picks a set of three numbers (0-255) where one has to be over minB
def randBright():
    notbright = True
    pick = 0
    while notbright:
        pick = (random.randrange(255), random.randrange(255), random.randrange(255))
        if max(pick) > minB:
            notbright = False
    return pick


# distance function
def distance(a, m):
    return math.sqrt((a[0] - m[0]) ** 2 + (a[1] - m[1]) ** 2)


# add the values of lists with 2 elements
def addL(z, y):
    return [z[0] + y[0], z[1] + y[1]]


# generates random colors
def genRandColors(k, clrs):
    for z in range(k):
        clrs.append(randBright())


# generates random data
def genRandData(datasize, rng, dta, typ):
    if typ == 0:
        rad = 60
        numb = 7
        randomPoints = []
        for a in range(numb):
            ranX = random.randrange(rad, resX - rad)
            ranY = random.randrange(rad, resY - rad)
            randomPoints.append([ranX, ranY])
        for a in range(datasize):
            ranP = random.randrange(numb)
            # picks a random angle and radius around the mouse cursor and then puts a data point there
            randA = (2 * pi) * (random.randrange(50) / 50)
            randR = random.randrange(rad)
            data.append(
                [randomPoints[ranP][0] + randR * math.cos(randA), randomPoints[ranP][1] + randR * math.sin(randA)])
    if typ == 1:
        for y in range(datasize):
            dta.append([resX * (random.randrange(rng) / rng), resY * (random.randrange(rng) / rng)])


# initializes the centroids to random points
def initkMeans(dta, k, cen, datasize):
    for m in range(k):
        idx = random.randrange(datasize)
        cen.append(dta[idx])


# Assigns the distances from each point to every centroid and then assigns belonging
def kMeansAssignCentroids(dta, k, cen, cD, cB, dS):
    # the nth element in cD is the distances of the nth point from the each centroid
    for z in range(dS):
        for y in range(k):
            cD[z].append(distance(cen[y], dta[z]))
    # finds the which centroid the minimum distance belongs to, the nth element in cB is the number of the centroid

    for z in cD:
        try:
            cB.append(z.index(min(z)))  # the nth element in cB is which centroid the nth data point belongs to
        except ValueError:
            break


# updates the position of each centroid to the average of their family
def kMeansUpdateCentroids(dta, k, cen, cB, dS, fS):
    # history for the trails
    for n, h in enumerate(cen):
        hold = (h[0], h[1])
        centHist[n].append(hold)
    sumhold = []

    # have to convert the data from screen position to cartesian coordinates
    dataconv = []
    for c in dta:
        dataconv.append([c[0] - resX / 2, c[1] - resY / 2])
    for h in range(k):
        sumhold.append([0, 0])

    # counting the number of points belonging to each centroid
    for h in cB:
        fS[h] += 1

    # summing the points belonging to each centroid
    for h in range(dS):
        sumhold[cB[h]] = addL(sumhold[cB[h]], dataconv[h])

    # finishing the average and then converting back to screen position
    for h in range(k):
        if not fS[h] == 0:
            cen[h] = [sumhold[h][0] / fS[h] + resX / 2, sumhold[h][1] / fS[h] + resY / 2]


# initialize the data
genRandColors(noK, colors)
genRandData(dSize, rnge, data, 1)
initkMeans(data, noK, centroids, dSize)
kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

# initialize surface and start the main loop
surface = pygame.display.set_mode((resX + UI, resY))
pygame.display.set_caption('K-Means')
running = True
# --------------------------------------- Main Loop ---------------------------------------
while running:
    mouse = pygame.mouse.get_pos()  # puts the mouse position into a 2d tuple
    familyHold = familySize  # necessary for the "this centroid has x members" display

    # drawing and erasing data come first because executing the processing and rendering of data comes after this code
    if drawing and mouse[0] + Rad < resX:  # code that handles the drawing in draw mode
        steps = 0
        for x in range(brushDen):
            # picks a random angle and radius around the mouse cursor and then puts a data point there
            randAng = (2 * pi) * (random.randrange(50) / 50)
            randRad = random.randrange(Rad)
            data.append([mouse[0] + randRad * math.cos(randAng), mouse[1] + randRad * math.sin(randAng)])
            dSize += 1

    if erasing:  # code that handles the erasing in draw mode
        steps = 0
        # finds which points are within the radius of the cursor and deletes them
        for p in data:
            if distance(p, mouse) < Rad:
                centBel.pop(data.index(p))
                data.pop(data.index(p))
                dSize -= 1

    # ------------------------------------- input handling -------------------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        # ------------------------------------ mouse click actions ------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and mouse[0] < resX:

            if not drawMode:  # centroid mode click actions
                if event.button == 1:  # left click add centroid
                    steps = 0
                    noK += 1
                    centroids.append(mouse)
                    familySize.append(0)
                    colors.append(randBright())
                    centDist = []
                    for x in range(dSize):
                        centDist.append([])
                    centBel = []
                    centHist = []
                    for x in range(noK):
                        centHist.append([])
                    kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

                if event.button == 3 and noK > 0:  # right click delete centroid
                    steps = 0
                    mouseDist = []
                    for p in centroids:
                        mouseDist.append(distance(p, mouse))
                    minDist = min(mouseDist)
                    closest = mouseDist.index(minDist)
                    noK -= 1
                    centroids.pop(closest)
                    familySize.pop(closest)
                    colors.pop(closest)
                    centDist = []
                    centHist = [[]]
                    for x in range(noK):
                        centHist.append([])
                    for x in range(dSize):
                        centDist.append([])
                    centBel = []
                    kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

            if drawMode:  # draw mode mouse actions
                steps = 0
                if event.button == 1:  # left click drawing
                    drawing = True
                if event.button == 3:  # right click erasing
                    erasing = True
        if event.type == pygame.MOUSEBUTTONUP:  # releasing the hold
            drawing = False
            erasing = False
        # ------------------------------------ key press actions ------------------------------------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:  # change random data type
                dType += 1
                dType %= 2
            if event.key == pygame.K_g:  # generate random data
                dSize = oSize
                data = []
                colors = []
                centroids = []
                centHist = []
                for x in range(noK):
                    centHist.append([])
                centDist = []
                steps = 0
                stepsT = 0
                for x in range(dSize):
                    centDist.append([])
                centBel = []
                genRandColors(noK, colors)
                genRandData(dSize, rnge, data, dType)
                initkMeans(data, noK, centroids, dSize)
                kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

            if event.key == pygame.K_s and dSize and noK:  # take step of k means
                kMeansUpdateCentroids(data, noK, centroids, centBel, dSize, familySize)
                centDist = []
                steps += 1
                stepsT += 1
                for i in range(dSize):
                    centDist.append([])
                centBel = []
                familySize = []
                for i in range(noK):
                    familySize.append(0)
                kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

            if event.key == pygame.K_q and dSize > 0:  # increase number of centroids
                steps = 0
                noK += 1
                ind = random.randrange(dSize)
                centroids.append(data[ind])
                familySize.append(0)
                colors.append(randBright())
                centDist = []
                for x in range(dSize):
                    centDist.append([])
                centBel = []
                centHist = []
                for x in range(noK):
                    centHist.append([])
                kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

            if event.key == pygame.K_a and noK > 0:  # decrease number of centroids
                steps = 0
                noK -= 1
                centroids.pop(-1)
                familySize.pop(-1)
                colors.pop(-1)
                centDist = []
                centHist = [[]]
                for x in range(noK):
                    centHist.append([])
                for x in range(dSize):
                    centDist.append([])
                centBel = []
                kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

            if event.key == pygame.K_t:  # toggle trails
                if trails:
                    trails = False
                    centHist = [[]]
                    for x in range(noK):
                        centHist.append([])
                else:
                    trails = True

            if event.key == pygame.K_x:  # toggle draw mode
                if drawMode < 1:
                    drawMode += 1
                else:
                    # updates centroid distances so the color is right (there is a more efficient way to do this, for the future)
                    centDist = []
                    for i in range(dSize):
                        centDist.append([])
                    centBel = []
                    familySize = []
                    for i in range(noK):
                        familySize.append(0)
                    kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)
                    drawMode = 0

            if event.key == pygame.K_c:  # change the color of the nearest centroid or clear the data lol
                if drawMode:  # clears data
                    steps = 0
                    stepsT = 0
                    dSize = 0
                    noK = 0
                    data = []
                    colors = []
                    centroids = []
                    centHist = []
                    for x in range(noK):
                        centHist.append([])
                    centDist = []
                    steps = 0
                    stepsT = 0
                    for x in range(dSize):
                        centDist.append([])
                    centBel = []
                elif noK > 0:  # changes the color of the nearest centroid
                    mouseDist = []
                    for p in centroids:
                        mouseDist.append(distance(p, mouse))
                    minDist = min(mouseDist)
                    closest = mouseDist.index(minDist)
                    colors[closest] = randBright()

            if drawMode:  # adjust brush radius and density
                if event.key == pygame.K_e:
                    Rad += 2
                if event.key == pygame.K_d and Rad > 3:
                    Rad -= 2
                if event.key == pygame.K_r:
                    brushDen += 2
                if event.key == pygame.K_f and brushDen > 3:
                    brushDen -= 2

            if event.key == pygame.K_w:  # randomly assign centroids
                centroids = []
                centHist = []
                for x in range(noK):
                    centHist.append([])
                centDist = []
                steps = 0
                stepsT = 0
                for x in range(dSize):
                    centDist.append([])
                centBel = []
                initkMeans(data, noK, centroids, dSize)
                kMeansAssignCentroids(data, noK, centroids, centDist, centBel, dSize)

    # ---------------------------------------- Rendering ----------------------------------------
    surface.fill((0, 0, 0))  # resets the screen to black

    # this displays data points
    for i in range(dSize):
        try:
            pygame.draw.circle(surface, colors[centBel[i]], data[i], radius)
        except IndexError:
            pygame.draw.circle(surface, (255, 255, 255), data[i], radius)

    # this displays trails
    if trails:
        noLines = 0
        for i, v in enumerate(centHist):
            for b in range(len(v) - 1):
                pygame.draw.line(surface, (255, 255, 255), v[b], v[b + 1], 2)
            try:
                pygame.draw.line(surface, (255, 255, 255), v[-1], centroids[i], 2)
            except IndexError:
                break



    # this highlights the closest centroid
    mouseDist = []
    if mouse[0] < resX:
        for p in centroids:
            mouseDist.append(distance(p, mouse))
        try:
            minDist = min(mouseDist)
            closest = mouseDist.index(minDist)
            pygame.draw.circle(surface, (255, 255, 255), centroids[closest], 15, width=3)
        except ValueError:
            pass

    # this displays the circle around the cursor
    if drawMode:
        for p in data:
            if distance(p, mouse) < Rad:
                pygame.draw.circle(surface, (255, 255, 255), p, radius)
        pygame.draw.circle(surface, (255, 255, 255), mouse, Rad, width=1)

    # this displays the centroids
    if dSize > 0:
        for i in range(noK):
            try:
                pygame.draw.rect(surface, colors[i], (centroids[i][0] - 5, centroids[i][1] - 5, 10, 10))
                pygame.draw.rect(surface, (255, 255, 255), (centroids[i][0] - 5, centroids[i][1] - 5, 10, 10), width=1)
            except IndexError:
                break

    # this displays the white line that divides points from the UI
    pygame.draw.line(surface, (255, 255, 255), (resX, 0), (resX, resY), 2)

    T = 10  # distance of text from top
    L = 10  # distance of text from left
    B = 15  # distance of text from bottom
    S = 25  # separation between text lines

    # text that tells you information
    UItext = [
        ["G to generate random data.",
         "D to change random data type.",
         "Current : " + ("True Random" if dType else "Clusters"),
         "S to take a step of k-means.",
         "Q to randomly add another centroid.",
         "A to delete most recent centroid.",
         "W to randomly assign centroids.",
         "T to toggle trails: " + ("(ON)" if trails else "(OFF)"),
         "X to toggle Centroid / Draw Modes."],
        ["Draw Mode",
         "Left click to draw data.",
         "Right click to remove data.",
         "C to clear all data.",
         "E/D to increase/decrease brush size.",
         "R/F to increase/decrease brush density."] if drawMode else
        ["Centroid Mode",
         "Left click to add a centroid.",
         "Right click to remove nearest centroids.",
         "C to change the color of the nearest centroid."]
    ]

    # text that tells you about the status of the program
    statusText = ["Draw mode : " + ("on" if drawMode else "off"),
                  f"Brush size : {Rad} | Brush density : {brushDen}",
                  f"Steps in total : {stepsT}",
                  f"Steps in this iteration : {steps}",
                  f"Number of points : {dSize}",
                  f"Number of centroids : {noK}"]

    # this displays the top set of text
    count = 0
    for box in UItext:
        for lines in box:
            text = font.render(lines, True, (255, 255, 255))
            surface.blit(text, (resX + L, T + S * count))
            count += 1


    # this displays the bottom set of text
    count = 1
    for lines in statusText:
        text = font.render(lines, True, (255, 255, 255))
        surface.blit(text, (resX + L, resY - (S * count)))
        count += 1

    pygame.display.flip()
