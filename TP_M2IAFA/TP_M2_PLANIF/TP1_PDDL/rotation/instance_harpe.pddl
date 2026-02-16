(define (problem harpe)

  (:domain rotation)

  (:objects
    p1 p2 p3 p4 p5 - position
    h a r p e - value
  )

  (:init
    (next p1 p2)
    (next p2 p3)
    (next p3 p4)
    (next p4 p5)
    (occurence h p1)
    (occurence a p2)
    (occurence r p3)
    (occurence p p4)
    (occurence e p5)
    (= (total-cost) 0)
  )

  (:goal
    (and
    (occurence p p1)
    (occurence h p2)
    (occurence a p3)
    (occurence r p4)
    (occurence e p5)
    )
  )
  (:metric minimize (total-cost))
)