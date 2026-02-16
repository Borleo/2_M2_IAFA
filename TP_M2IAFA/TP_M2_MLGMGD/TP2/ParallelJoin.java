import java.sql.Statement;
import java.sql.Connection;
import java.sql.ResultSet;

import java.util.ArrayList;
import java.util.List;


class Relation {
    int w, x, y, z;
    boolean bool;

    Relation(int x, int y) {
        this.x = x;
        this.y = y;
    }

    Relation(int w, int x, int y, int z, boolean bool) {
        this.w = w;    
        this.x = x;
        this.y = y;
        this.z = z;
        this.bool = bool;
    }

    @Override
    public String toString() {
        return "(" + x + ", " + y + ", " + z + ")";
    }
}

class JoinTask implements Runnable {
    private List<Relation> data;
    private List<Relation> result;
    private boolean evenY;

    public JoinTask(List<Relation> data, List<Relation> result, boolean evenY) 
       {
        this.data= data;
        this.result = result;
        this.evenY = evenY;
       }

    @Override
    public void run() {
        for (Relation d: data) {
            if (d.x == d.y) 
            {
                synchronized (result) 
                {
                System.out.println("Match jointure: (" + d.x + " = " + d.y +  ", " +evenY+")");
                result.add(new Relation(d.w, d.x, d.y, d.z, evenY));
               }
            }
        }
    }
}

public class ParallelJoin {

    // Créer une instance de OtherClass
    Connection connection = null;
    Statement statementR = null;
    Statement statementS = null;

    List<Relation> nodeA = new ArrayList<>();
    List<Relation> nodeB = new ArrayList<>();

    public void splitData(){
        try 
          {
            this.connection = IntializefeedJDBC.DBConnect();
            this.statementR = this.connection.createStatement() ;
            this.statementS = this.connection.createStatement() ;

            // Exécuter la requête pour la table R
            System.out.println("Données de la table R :");
            String queryR = "SELECT  X, Y FROM R";
            ResultSet resultSetR = this.statementR.executeQuery(queryR);

            // Exécuter la requête pour la table S
            System.out.println("\nDonnées de la table S :");
            String queryS = "SELECT  Y, Z FROM S";            

            while (resultSetR.next()) {
                // Traitement des données
                int Xr = resultSetR.getInt("X"); // Remplacez par les colonnes réelles de la table R
                int Yr = resultSetR.getInt("Y"); // Exemple : une colonne "value"

                System.out.println(" Xr : "+ Xr +"  |  " + "Yr : " + Yr);   
                ResultSet resultSetS = statementS.executeQuery(queryS);
                while (resultSetS.next()) { 
                    // Traitement des données
                    int Ys = resultSetS.getInt("Y"); // Remplacez par les colonnes réelles de la table S
                    int Zs = resultSetS.getInt("Z"); // Exemple : une colonne "description"

                    if ((Yr % 2 == 0) && (Yr == Ys)) {
                        nodeA.add(new Relation(Xr, Yr, Ys, Zs,true));   
                        System.out.println("add nodeA Xr : "+ Xr +"  |  " + "Yr : " + Yr + " Ys : "+ Ys +"  |  " + "Zs : " + Zs); 
                    }
                    else if ((Yr % 2 != 0) && (Ys == Yr)){ 
                        nodeB.add(new Relation(Xr, Yr, Ys, Zs,false));
                        System.out.println("add nodeB Xr : "+ Xr +"  |  " + "Yr : " + Yr + " Ys : "+ Ys +"  |  " + "Zs : " + Zs); 
                    }
                 } 
            }  
            System.out.println("NodeA : "+nodeA);   
            System.out.println("NodeB : "+nodeB);        
        } 
        catch (Exception e) 
            {
            e.printStackTrace();
            }

    }

    public static void main(String[] args) throws InterruptedException {

        ParallelJoin paralleljoin = new ParallelJoin();
        paralleljoin.splitData();
        List<Relation> result = new ArrayList<>();

        Thread threadEven = new Thread(new JoinTask(paralleljoin.nodeA, result, true));
        Thread threadOdd = new Thread(new JoinTask(paralleljoin.nodeB , result, false));

        threadEven.start();
        threadOdd.start();

        threadEven.join();
        threadOdd.join();

        System.out.println("Résultat de la jointure :");
        for (Relation res : result) {
            System.out.println("(" + res.x + ", " + res.y + ", " + res.z + ", " + res.bool + ")");
        }
    }
}


