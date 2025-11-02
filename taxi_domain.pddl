(define (domain taxi)
    (:requirements :strips :typing)

    (:types
        location
        taxi
        passenger
    )

    (:predicates    (taxi-at ?taxi - taxi ?loc - location)
                    (passenger-at ?passenger - passenger ?loc - location)
                    (in-taxi ?passenger - passenger ?taxi - taxi)
                    (adjacent ?loc1 ?loc2 - location)
                    (destination ?passenger - passenger ?loc - location)
                    (north ?origin ?destination - location)
                    (south ?origin ?destination - location)
                    (east ?origin ?destination - location)
                    (west ?origin ?destination - location)
    )

    (:action PICK-UP
        :parameters     (?t - taxi ?p - passenger ?loc - location)
        :precondition   (and (taxi-at ?t ?loc)
                        (passenger-at ?p ?loc)
                        (not (in-taxi ?p ?t)))

        :effect         (and (not (passenger-at ?p ?loc)) (in-taxi ?p ?t))
    )

    (:action DROP-OFF
        :parameters     (?t - taxi ?p - passenger ?loc - location)
        :precondition   (and (in-taxi ?p ?t)
                        (taxi-at ?t ?loc)
                        (destination ?p ?loc))
        :effect         (and (not (in-taxi ?p ?t))
                        (passenger-at ?p ?loc))
    )

    (:action MOVE-NORTH
        :parameters     (?t - taxi ?origin ?destination - location)

        :precondition   (and (taxi-at ?t ?origin)
                        (north ?origin ?destination))

        :effect         (and (not (taxi-at ?t ?origin))
                        (taxi-at ?t ?destination))
    )

    (:action MOVE-SOUTH
        :parameters     (?t - taxi ?origin ?destination - location)

        :precondition   (and (taxi-at ?t ?origin)
                        (south ?origin ?destination))

        :effect         (and (not (taxi-at ?t ?origin))
                        (taxi-at ?t ?destination))
    )

    (:action MOVE-WEST
        :parameters     (?t - taxi ?origin ?destination - location)

        :precondition   (and (taxi-at ?t ?origin)
                        (west ?origin ?destination))

        :effect         (and (not (taxi-at ?t ?origin))
                        (taxi-at ?t ?destination))
    )

    (:action MOVE-EAST
        :parameters     (?t - taxi ?origin ?destination - location)

        :precondition   (and (taxi-at ?t ?origin)
                        (east ?origin ?destination))

        :effect         (and (not (taxi-at ?t ?origin))
                        (taxi-at ?t ?destination))
    )


)