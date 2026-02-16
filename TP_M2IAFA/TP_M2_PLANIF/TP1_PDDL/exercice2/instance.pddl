(define (problem problem-exercice2)

  (:domain exercice2)

  (:objects
    keyA keyB - key
    vaultA vaultB - vault
    roomS roomVA roomKA roomVB roomKB - room
  )

  (:init
    (connected roomS roomVA)
    (connected roomS roomKB) 
    (connected roomVA roomKA)
    (connected roomKB roomVB) 
    (at-key keyA roomKA)      ;; la présence de la clé A dans la pièce KA
    (at-key keyB roomKB)      ;; la présence de la clé B dans la pièce KB
    (at-door vaultA roomVA)   ;; la présence du coffre A dans la pièce VA
    (at-door vaultB roomVB)   ;; la présence du coffre B dans la pièce VB
    (at-robot roomS)          ;; la présence du robot dans la pièce S
    (empty-hand)              ;; le robot à la main vide
  )

  (:goal (and
    (open vaultA)             ;; le coffre A est ouvert 
    (open vaultB)             ;; le coffre B est ouvert 
    (empty-hand)              ;; le robot à la main vide
    (at-robot roomS)          ;; la présence du robot dans la pièce S
  ))
)
