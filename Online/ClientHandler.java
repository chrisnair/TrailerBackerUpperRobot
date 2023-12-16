package Online;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.util.ArrayList;
import java.util.UUID;

/**
 *
 * Used by the server to handle the inputs and outputs of connected clients.
 * This is how the server communicates to its clients
 *
 * @author Joshua Bergthold
 */
public class ClientHandler extends OnlineObject {

    /**
     * The "parent" server of this handler, this is what the handler will report to
     */
    private final Server serv;

    /**
     * Creates a ClientHandler instance that uses the given Socket resource as the
     * I/O
     * 
     * @param s    the socket to be used for the I/O of this handler
     * @param serv the server that made this ClientHandler
     */
    public ClientHandler(Socket s, Server serv) {
        super(serv.getID());
        initializeSocket(s);
        this.serv = serv;
        isListening = false;
        setDefaultPacketProcessor();

        onJoin();
    }

    @Override
    protected void sendInitialAssignmentsToCaller() {
        Printer.debugPrint("Assigning caller an ID");
        super.sendInitialAssignmentsToCaller();
        assignCaller(DefaultOnlineCommands.ID_FLAG, serv.generateNewID());
    }

    /**
     * Sets the packet processor of this object to the default
     * This method can be overridden if you want a different packet processor to go
     * with this OnlineObject
     */
    public void setDefaultPacketProcessor() {
        processor = new ServerPacketProcessor(this);
    }

    /**
     * Tells the server to send a packet to all of its clients
     * 
     * @param p Packet to be distributed across the server's clients
     */
    public void sendForServerToDistribute(Packet p) {
        serv.sendPacketToAllClients(p);
    }

    @Override
    public UUID getID() {
        return serv.getID();
    }

    public void sendPacketToOutput(Packet p){
        serv.sendPacketToOutput(p);
    }

    @Override
    public void leave() {
        Printer.debugPrint("Leave called");
        super.leave();
        serv.disconnectClient(this);
    }

}
