import java.sql.*;
import oracle.jdbc.pool.*;

//CREATE USER gerard IDENTIFIED BY gbenitah;
//GRANT CREATE SESSION TO gerard;
//GRANT RESOURCE TO gerard;
//SELECT username, account_status FROM dba_users WHERE username = 'GERARD';
//ALTER USER gerard QUOTA UNLIMITED ON USERS;
//docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 63f8679fb619
//String url = "jdbc:oracle:thin:@telline.univ-tlse3.fr:1521:etupre"; user = "BNG8016A", pw = "gerard"; 

public class IntializefeedJDBC {
	
	// Afficher un message avec le nom du thread
    static void threadMessage(String message) 
	{
        String threadName =
            Thread.currentThread().getName();
        System.out.format("%s: %s%n",
                          threadName,
                          message);
    }
	
	static Connection DBConnect()
	{
		Connection conn = null;
		String user = "gerard";
		String pwd = "gbenitah";
		String url = "jdbc:oracle:thin:@//localhost:1521/ORCLPDB1";	
		try 
		{
        	//Declarer un objet OracleDataSource (version JDBC >=4)
			OracleDataSource ods = new OracleDataSource();
			
			//Definir les parametres de connexion pour l'objet ods
			ods.setURL(url);
			ods.setUser(user);
			ods.setPassword(pwd);
			
			//Apple de la methode getConnection() pour obtenir une connextion
			conn = ods.getConnection();
			threadMessage("Vous etes connecte.");
		} 
		catch(SQLException ods)
		{
			threadMessage(ods.getMessage());
		}
		
		return conn;		
	}	


	public static void main(String[] args) throws InterruptedException{
		Connection conn = null;
		Statement stmt = null;
		ResultSet rst = null;
		//Connexion
        conn = DBConnect();			
		//Creer la relation R
		try
			{
			String dropR = "drop table R";
			stmt = conn.createStatement();
			try
				{
				stmt.executeUpdate(dropR);
				} 
			catch(SQLException sqldrop)
				{
				threadMessage(sqldrop.getMessage());
				}
			String createR = "create table R(X number(1), Y number(1))";
			stmt.executeUpdate(createR);
			threadMessage("Relation R cree.");
			}
		catch(SQLException sqlcreation)
			{
			threadMessage(sqlcreation.getMessage());
			} 

		//Creer la relation S
		try
			{
			String dropS = "drop table S";
			stmt = conn.createStatement();
			try
				{
				stmt.executeUpdate(dropS);
				} 
			catch(SQLException sqldrop)
				{
				threadMessage(sqldrop.getMessage());
				}
			String createS = "create table S(Y number(1), Z number(1))";
			stmt.executeUpdate(createS);
			threadMessage("Relation S cree");
			}
		catch(SQLException sqlcreation)
		{
			threadMessage(sqlcreation.getMessage());
		}
			
		//Inserer les tuples de R
		try{
			String insertR_t1 = "insert into R values(1,1)";
			String insertR_t2 = "insert into R values(1,2)"; 
			String insertR_t3 = "insert into R values(1,3)"; 
			String insertR_t4 = "insert into R values(1,4)";
			String insertR_commit = "commit";
			stmt.executeUpdate(insertR_t1);
			stmt.executeUpdate(insertR_t2);
			stmt.executeUpdate(insertR_t3);
			stmt.executeUpdate(insertR_t4);
			stmt.executeUpdate(insertR_commit);
			threadMessage("les tuples de R sont inseres.");
		}
		catch(SQLException sqlinsertion){
			threadMessage(sqlinsertion.getMessage());
		}
			
		//Inserer les tuples de S
		try
		{
			String insertS_t1 = "insert into S values(1,2)";
			String insertS_t2 = "insert into S values(2,7)"; 
			String insertS_t3 = "insert into S values(3,9)"; 
			String insertS_t4 = "insert into S values(4,3)";
			String insertS_commit = "commit";
			stmt.executeUpdate(insertS_t1);
			stmt.executeUpdate(insertS_t2);
			stmt.executeUpdate(insertS_t3);
			stmt.executeUpdate(insertS_t4);
			stmt.executeUpdate(insertS_commit);
			threadMessage("les tuples de S sont inseres.");
		}
		catch(SQLException sqlinsertion){
			threadMessage(sqlinsertion.getMessage());
		}			
		// afficher les tuples de R et S
		try
			{
			Boolean nonvide;
			nonvide = stmt.execute("select * from R");
			if(nonvide)
				{
				rst = stmt.getResultSet();
				System.out.println("Relation R :");
				System.out.println("X    Y");
				while(rst.next())
					{
					int x = rst.getInt("X");
					int y = rst.getInt("Y");
					System.out.println(x + "    " + y);
					}
			}
			try
				{
				rst.close();
				} 
			catch(SQLException se)
				{
					threadMessage(se.getMessage());
				}			
			nonvide = stmt.execute("select * from S");
			if(nonvide)
				{
				rst = stmt.getResultSet();
				System.out.println("Relation S :");
				System.out.println("Y    Z");
				while(rst.next())
					{
					int x = rst.getInt("Y");
					int y = rst.getInt("Z");
					System.out.println(x + "    " + y);
					}
				}
			}		
		catch(SQLException sqlQueryError)
			{
			threadMessage(sqlQueryError.getMessage());
			}
		finally
			{
			try
				{
				stmt.close();
				rst.close();
				if(conn != null)
					conn.close();
				threadMessage("Connextion fermee.");
				}
			catch(SQLException se){
				threadMessage(se.getMessage());
			}
		}
	}
}

