(define (problem guerison)
  (:domain rotation)
  (:objects
    p1 p2 p3 p4 p5 p6 p7 p8 - position
    g  u  e  r  i  s  o  n  - value
  )

  (:init
    (next p1 p2)
    (next p2 p3)
    (next p3 p4)
    (next p4 p5)
    (next p5 p6)
    (next p6 p7)
    (next p7 p8)
    (occurence g p1)
    (occurence u p2)
    (occurence e p3)
    (occurence r p4)
    (occurence i p5)
    (occurence s p6)
    (occurence o p7)
    (occurence n p8)    
    (= (total-cost) 0)
  )

  (:goal
    (and
    (occurence s p1)
    (occurence o p2)
    (occurence i p3)
    (occurence g p4)
    (occurence n p5)
    (occurence e p6)
    (occurence u p7)
    (occurence r p8)
    )
  )
  (:metric minimize (total-cost))
)