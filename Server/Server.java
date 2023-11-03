package Online;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.*;

/**
 *
 * A server controls the joining of clients and processing of client data
 *
 * @author Joshua Bergthold
 */
public class Server{


    /**
     * Default address that is used when none is given
     */
    public static final String DEFAULT_ADDRESS = "localhost";
    /**
     * Default port that is used when none is given
     */
    public static final int DEFAULT_PORT = 1452;

    /**
     * ServerSocket that dispatches Sockets to ClientHandlers
     */
    ServerSocket ss;
    /**
     * Keeps track of the active Clients with a connection
     */
    protected LinkedList<ClientHandler> clientList;
    /**
     * If the server is running or not
     */
    private boolean running;
    /**
     * Port that the server is running on
     */
    private final int port;

    public ArrayList<UUID> validIDs;

    private final UUID id;

    Thread connectionListener;



    /**
     * Constructs a Server object with the default port (1452)
     */
    public Server(){
        this(1452);
    }

    /**
     * Constructs a Server with a specified port
     * @param port desired port of the server
     */
    public Server(int port){
        this.port = port;
        this.clientList = new LinkedList<>();
        this.validIDs = new ArrayList<>();
        this.id = UUID.randomUUID();
        initializeServer();

    }

    /**
     * Creates the underlying ServerSocket which has the ability to make Client connections
     */
    private void initializeServer(){
        try {
            this.ss = new ServerSocket(this.port);
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    /**
     * Begins the server loop and creates threads for listening for Clients and processing data received
     */
    public void start(){
        running = true;
        listenForConnections();
    }

    /**
     * Starts the thread that constantly looks for Clients attempting a connection to the Server
     */
    private void listenForConnections(){
        Runnable r = () -> {
            Printer.printIfVerbose("Starting listening for connections");
            while(running){
                try{
                   ClientHandler c = initializeClientHandler(ss.accept());
                   addClient(c);
                   Printer.printIfVerbose("New client joined.");
                   c.startProcessingPackets();
                } catch(IOException e){
                    Printer.errorPrintIfVerbose("Error during creation of server");
                    e.printStackTrace();
                    System.exit(1);
                }

            }
        };

        connectionListener = new Thread(r);
        connectionListener.setName("Connection Listener");
        connectionListener.start();
    }

    /**
     * Override this method to change what kind of handlers this server creates
     * @param s Socket that the handler is given
     * @return the ClientHandler that was initialized
     */
    protected ClientHandler initializeClientHandler(Socket s){
        return new ClientHandler(s, this);

    }

    /**
     * Adds a ClientHandler to this server
     * @param c client to be added
     */
    protected void addClient(ClientHandler c){
        clientList.add(c);
    }


    /**
     * Takes a packet and sends it to every client this server has connected
     * @param p packet to be distributed
     */
    public void sendPacketToAllClients(Packet p){
        for(ClientHandler c: clientList){
            c.sendMessage(p);
        }
    }


    /**
     *
     * @return true if the server is running
     */
    public boolean isRunning(){
        return running;
    }


    /**
     * @return the ID of this server
     */
    public UUID getID() {
        return this.id;
    }


    /**
     * Disconnects a client and removes them from the server
     * @param c client to be disconnected
     */
    public void disconnectClient(ClientHandler c){
        clientList.remove(c);

        boolean handlerRemoved = validIDs.remove(c.getID());
        boolean clientRemoved = validIDs.remove(c.getCallerID());
        Printer.printIfVerbose(validIDs);
        Printer.printIfVerbose("Handler ID was " + (handlerRemoved ? "": "not") + "removed");
        Printer.printIfVerbose("Client ID was " + (clientRemoved ? "": "not") + "removed");
        Printer.printIfVerbose(validIDs);
        c.disconnect();
    }

    /**
     * Stops the server and disconnects all of its clients
     */
    public void stop(){
        System.out.println("Stopping server...");
        for(ClientHandler c: clientList){
            disconnectClient(c);

        }
        connectionListener.interrupt();


    }

    public UUID generateNewID(){
        UUID newID = UUID.randomUUID();
        validIDs.add(newID);
        return newID;
    }


}
