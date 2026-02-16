(define (problem chien)

  (:domain rotation)

  (:objects
    p1 p2 p3 p4 p5 - position
    c h i e n - value
  )

  (:init
    (next p1 p2)
    (next p2 p3)
    (next p3 p4)
    (next p4 p5)
    (occurence c p1)
    (occurence h p2)
    (occurence i p3)
    (occurence e p4)
    (occurence n p5)
    (= (total-cost) 0)
  )

  (:goal
    (and
    (occurence n p1)
    (occurence i p2)
    (occurence c p3)
    (occurence h p4)
    (occurence e p5)
    )
  )
  (:metric minimize (total-cost))
)
