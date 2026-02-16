(define (domain gripper)

  (:requirements
    :typing
  )

  (:types
    ball room
  )

  (:predicates
    (at-ball ?b - ball ?r - room)    ;; true if b is a ball, r is a room, and b is in r
    (at-robby ?r - room)             ;; true if r is a room and the robot is in r
    (carry ?b - ball)                ;; true if b is a ball and gripper holds b 
    (hand-free)                      ;; true if gripper does not hold a ball
  )

   (:action pick
    :parameters (?b - ball ?from  - room)
    :precondition (and (hand-free) (at-ball ?b ?from)  (at-robby ?from) )
    :effect (and (carry ?b)  (not(hand-free)) (not (at-robby ?from))  )
   )
  (:action move
    :parameters (?x ?y - room)
    :precondition (and (at-robby ?x) (not(at-robby ?y)))
    :effect (and (at-robby ?y) (not (at-robby ?x)))
  )
  
   (:action drop
    :parameters (?b - ball ?to - room )
    :precondition (and ( (carry ?b)  (at-robby ?to))    
    :effect (and (hand-free) (not (carry ?b)) (at-ball ?b ?to) )
   )  
  
)
