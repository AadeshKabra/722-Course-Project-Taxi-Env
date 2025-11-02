(define (problem taxi-problem-01)
    (:domain taxi)

    (:objects
        taxi1 - taxi
        loc-0-0 loc-0-1 loc-0-2 loc-0-3 loc-0-4
        loc-1-0 loc-1-1 loc-1-2 loc-1-3 loc-1-4
        loc-2-0 loc-2-1 loc-2-2 loc-2-3 loc-2-4
        loc-3-0 loc-3-1 loc-3-2 loc-3-3 loc-3-4
        loc-4-0 loc-4-1 loc-4-2 loc-4-3 loc-4-4 - location
        passenger1 - passenger
        red yellow green blue - destination
    )

    (:init
        (taxi-at taxi1 loc-0-0)
        (passenger-at passenger1 loc-0-4)
        (destination passenger1 loc-4-4)


        (east loc-0-0 loc-0-1)
        (west loc-0-1 loc-0-0)
        (east loc-0-1 loc-0-2)
        (west loc-0-2 loc-0-1)
        (east loc-0-2 loc-0-3)
        (west loc-0-3 loc-0-2)
        (east loc-0-3 loc-0-4)
        (west loc-0-4 loc-0-3)


        (east loc-1-0 loc-1-1)
        (west loc-1-1 loc-1-0)
        (east loc-1-1 loc-1-2)
        (west loc-1-2 loc-1-1)
        (east loc-1-2 loc-1-3)
        (west loc-1-3 loc-1-2)
        (east loc-1-3 loc-1-4)
        (west loc-1-4 loc-1-3)


        (east loc-2-0 loc-2-1)
        (west loc-2-1 loc-2-0)
        (east loc-2-1 loc-2-2)
        (west loc-2-2 loc-2-1)
        (east loc-2-2 loc-2-3)
        (west loc-2-3 loc-2-2)
        (east loc-2-3 loc-2-4)
        (west loc-2-4 loc-2-3)


        (east loc-3-0 loc-3-1)
        (west loc-3-1 loc-3-0)
        (east loc-3-1 loc-3-2)
        (west loc-3-2 loc-3-1)
        (east loc-3-2 loc-3-3)
        (west loc-3-3 loc-3-2)
        (east loc-3-3 loc-3-4)
        (west loc-3-4 loc-3-3)


        (east loc-4-0 loc-4-1)
        (west loc-4-1 loc-4-0)
        (east loc-4-1 loc-4-2)
        (west loc-4-2 loc-4-1)
        (east loc-4-2 loc-4-3)
        (west loc-4-3 loc-4-2)
        (east loc-4-3 loc-4-4)
        (west loc-4-4 loc-4-3)


        (south loc-0-0 loc-1-0)
        (north loc-1-0 loc-0-0)
        (south loc-1-0 loc-2-0)
        (north loc-2-0 loc-1-0)
        (south loc-2-0 loc-3-0)
        (north loc-3-0 loc-2-0)
        (south loc-3-0 loc-4-0)
        (north loc-4-0 loc-3-0)


        (south loc-0-1 loc-1-1)
        (north loc-1-1 loc-0-1)
        (south loc-1-1 loc-2-1)
        (north loc-2-1 loc-1-1)
        (south loc-2-1 loc-3-1)
        (north loc-3-1 loc-2-1)
        (south loc-3-1 loc-4-1)
        (north loc-4-1 loc-3-1)


        (south loc-0-2 loc-1-2)
        (north loc-1-2 loc-0-2)
        (south loc-1-2 loc-2-2)
        (north loc-2-2 loc-1-2)
        (south loc-2-2 loc-3-2)
        (north loc-3-2 loc-2-2)
        (south loc-3-2 loc-4-2)
        (north loc-4-2 loc-3-2)


        (south loc-0-3 loc-1-3)
        (north loc-1-3 loc-0-3)
        (south loc-1-3 loc-2-3)
        (north loc-2-3 loc-1-3)
        (south loc-2-3 loc-3-3)
        (north loc-3-3 loc-2-3)
        (south loc-3-3 loc-4-3)
        (north loc-4-3 loc-3-3)


        (south loc-0-4 loc-1-4)
        (north loc-1-4 loc-0-4)
        (south loc-1-4 loc-2-4)
        (north loc-2-4 loc-1-4)
        (south loc-2-4 loc-3-4)
        (north loc-3-4 loc-2-4)
        (south loc-3-4 loc-4-4)
        (north loc-4-4 loc-3-4)
    )

    (:goal (and
        (passenger-at passenger1 loc-4-4)
    ))
)