(define (problem rabachai)

  (:domain rotation)

  (:objects
    p1 p2 p3 p4 p5 p6 p7 p8 - position
    r  a  b  a  c  h  a  i  - value
  )

  (:init
    (next p1 p2)
    (next p2 p3)
    (next p3 p4)
    (next p4 p5)
    (next p5 p6)
    (next p6 p7)
    (next p7 p8)
    (occurence r p1)
    (occurence a p2)
    (occurence b p3)
    (occurence a p4)
    (occurence c p5)
    (occurence h p6)
    (occurence a p7)
    (occurence i p8)    
    (= (total-cost) 0)
  )

  (:goal
    (and
    (occurence c p1)
    (occurence h p2)
    (occurence a p3)
    (occurence r p4)
    (occurence a p5)
    (occurence b p6)
    (occurence i p7)
    (occurence a p8)
    )
  )
  (:metric minimize (total-cost))
)
