package Online;



import java.io.IOException;
import java.net.Socket;
import java.util.UUID;

/**
 * Clients are standalone OnlineObjects that connect to a server to communicate.
 * @author Joshua Bergthold
 */
public class Client extends OnlineObject {

    String address;
    int port;


    /**
     * Creates a client object that connects to a server with the specified port and address.
     * @param address IPv4 address of the server this client connects to
     * @param port Port that the client will connect to
     */
    public Client(String address, int port){
        super();
        setPacketProcessor();
        this.address = address;
        this.port = port;
    }

    public boolean attemptConnection(){
        try {
            establishConnection(address, port);
            return true;
        } catch (Exception e){
            return false;
        }
    }

    /**
     * Creates a client object that connects to a server with the specified address and with a default port (1452)
     * @param address IPv4 address of the server this client connects to
     */
    public Client(String address){
        this(address, 1452);
    }

    protected void setPacketProcessor(){
        processor = new ClientPacketProcessor(this);
    }


    /**
     * Creates a socket that connects to the given address and port, and blocks until it does so, otherwise it times out
     * @param address address to be connected to
     * @param port port to communicate on
     */
    private void establishConnection(String address, int port){
        //create a new socket that connects to the port and address
        //need to catch a couple of exceptions
        while (true) {
            try {
                System.out.println("Trying to connect");
                s = new Socket(address, port);
                System.out.println("Connected, initializing");
                initializeSocket(s);
                break;
            } catch (IOException e){
                try {
                    System.out.println("Failed trying again");
                    e.printStackTrace();
                    Thread.sleep(1000);
                } catch (InterruptedException ex) {
                    throw new RuntimeException(ex);
                }
                System.out.println("Connection refused, trying again");
            }
        }

    }

    public void sendGyroReading(double reading){
        if(isRunning()) {
            Packet p = new Packet(
                    DefaultOnlineCommands.CONTROL_SIGNAL + DefaultOnlineCommands.STEERING_ANGLE,
                    reading,
                    getID()
            );
            //Log.d("Sending gyroreading", "Packet constructed, sending...");
            this.sendAppData(p);
        }
    }

    @Override
    public void disconnect(){
        super.disconnect();

    }


    public void sendGasReading(double gasVal) {
        if(isRunning()){
            Packet p = new Packet(
                    DefaultOnlineCommands.CONTROL_SIGNAL + DefaultOnlineCommands.THROTTLE,
                    gasVal,
                    getID()
            );
            //Log.d("Sending gyroreading", "Packet constructed, sending...");
            this.sendAppData(p);
        }
    }

    public void requestCameraChange(boolean state){
        if(isRunning()){
            Packet p = new Packet(
                    DefaultOnlineCommands.DEBUG + DefaultOnlineCommands.CAMERA_MODE_CHANGE,
                    state? 1 : 0,
                    this.getID()
            );
            this.sendAppData(p);
        }

    }
}
