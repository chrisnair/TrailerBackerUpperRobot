package Online;

public class ServerStarter {
    public static void main(String[] args) {
        Server s = new Server(1102);
        s.start();

        // Printer.toggleDebugosity();
        // Printer.toggleVerbosity();
    }
}
