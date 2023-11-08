package Online;

public class ServerStarter {
    public static void main(String[] args) {
        Server serv = new Server(1102);
        serv.start();
        
    }
}
