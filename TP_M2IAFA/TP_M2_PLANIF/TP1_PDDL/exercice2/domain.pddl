(define (domain exercice2)

  (:requirements
    :typing
  )

  (:types
    key vault room
  )

  (:predicates
    (at-robot ?x - room)              ;; permet de localiser le robot
    (connected ?x ?y - room)          ;; permet de représenter les ar^êtes du graphe
    (at-key ?x - key ?y -  room)      ;; la présence d'une clé dans une pièce
    (at-door ?x - vault ?y - room)    ;; la présence d'un coffre dans une pièce
    (open ?x - vault)                 ;; le coffre est ouvert 
    (has-key)                         ;; le robot à une clé dans la main
    (empty-hand)                      ;; le robot à la main vide
  )

  (:action move
    :parameters (?x ?y - room)
    :precondition (and (at-robot ?x) (connected ?x ?y) )
    :effect  (and (at-robot ?y) (not(at-robot ?x)) ))

  (:action pick-key ;; permet au robot de ramasser la clé dans la pièce où il se trouve
    :parameters (?x - key ?y - room)
    :precondition (and (at-robot ?y)  (at-key ?x ?y)  (empty-hand) )
    :effect (and (not (empty-hand))  (has-key) (not(at-robot ?y)) ))
    
  (:action open-door ;; permet au robot d'ouvrir un coffre
    :parameters (?x - key ?y - vault ?z - room)
    :precondition (and (at-robot ?z)  (at-door ?y  ?z)  (has-key) )
    :effect (and (empty-hand) (open ?y) (not(at-robot ?z))  ))    
) 
