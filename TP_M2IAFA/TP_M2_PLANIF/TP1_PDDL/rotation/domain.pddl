(define (domain rotation)
  (:requirements
    :typing :action-costs
  )

  (:types
    position value
  )

  (:predicates
    (next ?n ?p - position)
    (occurence ?v - value ?p - position )
  )

  (:functions (total-cost) - number)

  (:action small-rotation
   :parameters (?v ?w - value ?n ?m - position)
    :precondition (and
        (next ?n ?m)
        (occurence ?v ?n)
        (occurence ?w ?m)
      )
    :effect (and
      (not (occurence ?v ?n))
      (not (occurence ?w ?m))
      (occurence ?w ?n)
      (occurence ?v ?m)
      (increase (total-cost) 1)
      ))
      
  (:action big-rotation
    :parameters (?v ?w ?x - value ?n ?m ?o - position)
    :precondition (and
        (next ?n ?m)
        (occurence ?v ?n)
        (occurence ?x ?o)
      )
    :effect (and
      (not (occurence ?v ?n))
      (not (occurence ?x ?o))
      (occurence ?v ?o)
      (occurence ?x ?n)
      (increase (total-cost) 1)
      ))      

)
