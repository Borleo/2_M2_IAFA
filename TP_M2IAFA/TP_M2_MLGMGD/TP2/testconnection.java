import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class testconnection {
    public static void main(String[] args) {
        String url = "jdbc:oracle:thin:@//localhost:1521/ORCLPDB1";
        String user = "gerard";
        String password = "gbenitah";

        try (Connection conn = DriverManager.getConnection(url, user, password)) {
            System.out.println("Connection successful!");
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
