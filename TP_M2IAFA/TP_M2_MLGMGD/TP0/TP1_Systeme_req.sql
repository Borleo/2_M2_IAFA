
ALTER TABLE EQUIPE DISABLE CONSTRAINT Key_Equipe CASCADE; 


--Créer la vue CHERCHEUR_2400 (CodeCh, NomCh, Salaire)  des chercheurs qui ont un salaire superieur e 2400 euros . 

create or replace view CHERCHEUR_2400 AS 
select codech, Nomch,codeeq, salaire 
from CHERCHEUR
where salaire> 2400;


--Créer un nouveau chercheur (15, Thierry, 2, 2600) dans la table CHERCHEUR.    Interroger la relation CHERCHEUR et la vue CHERCHEUR_2400. Que constatez-vous ?
insert into CHERCHEUR_2400 (codech, Nomch,codeeq, salaire )
VALUES (15, 'Thierry' , 2, 2600);

 

--Créer la vue CHERCHEUR_EQ1 (CodCh, NomCh,)  des chercheurs de leequipe de code 1.  
create or replace view CHERCHEUR_EQ1 AS 
select codech, Nomch, codeeq, salaire  
from CHERCHEUR
where codeeq =1;

--A partir de la vue CHERCHEUR_EQ1, lister la liste des chercheurs.  
select * from CHERCHEUR_EQ1;

--Inserer dans la relation CHERCHEUR  un nouveau chercheur (14, e RENAUD e, 1,1000) .
insert into CHERCHEUR_EQ1 (codech, Nomch,codeeq, salaire )
VALUES (14, 'RENAUD', 1,1000);

--A partir de CHERCHEUR_EQ1 : - lister les chercheurs de leequipe 1,
select * from CHERCHEUR_EQ1 where codeeq =1;

-- remplacer le nom RENAUD par RENAUDIN
update CHERCHEUR_EQ1
SET NOMCH ='RENAUDIN'
WHERE NOMCH ='RENAUD';

-- Inserer le chercheur (18, ee LALANDEee)
insert into CHERCHEUR_EQ1 (codech, Nomch,codeeq, salaire )
VALUES (18, 'LALANDE', '','');

-- Lister les chercheurs de leequipe 1. Que seest il passe ? detruire le chercheur eeLALANDEee
select * from CHERCHEUR_EQ1 where codeeq =1;


-- Créer la vue CHERCHEUR_EQUIPE (CodeCh, Nomch, NomEq, Resp_Eq)     
--Lister les chercheurs de leequipe FIRM. A  partir de cette vue,  tenter de faire des mises e jour. Commenter. 

create or replace VIEW CHERCHEUR_EQUIPE AS
SELECT c.CodeCh, c.Nomch, c2.Nomch AS Resp_Eq , e.NOMEQ
from chercheur c, chercheur c2, equipe e 
WHERE c.codeeq = e.codeeq and e.CODERESP = c.CODECH;


ALTER TABLE EQUIPE ENABLE CONSTRAINT Key_Equipe ; --pour sql

ALTER TABLE EQUIPE add CONSTRAINT pk_codee primary key (codeeq); --pour oracle

describe equipe;
