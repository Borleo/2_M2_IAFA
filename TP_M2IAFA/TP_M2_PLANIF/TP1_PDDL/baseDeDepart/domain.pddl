(define (domain domain-name)

  (:requirements
    :typing
  )

  (:types
    subtype1 subtype2 subtype3 - object
  )

  (:predicates
    (predicateName ?x - object ?y - object)
  )

  (:action action-name
    :parameters ()
    :precondition (and ())
    :effect (and ()))

) 

;; ./validate -v test-domain.pddl test-problem.pddl
;; ./plan test-domain.pddl test-problem.pddl test-solution.txt