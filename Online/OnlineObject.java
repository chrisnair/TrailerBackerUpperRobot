package Online;

import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.Socket;
import java.net.SocketException;
import java.util.UUID;

/**
 * Specifies what all "Online" entities should be able to do.
 * OnlineObjects can communicate over the internet and use PacketProcessors to carry out those messages
 *
 * @author Joshua Bergthold
 */
public abstract class OnlineObject {


    /**
     * This is the socket that this OnlineObject uses to connect its "caller"
     */
    protected Socket s;
    /**
     * The output stream of this OnlineObject, this is how it sends messages to its "caller"
     */
    protected ObjectOutputStream oos;
    /**
     * The input stream of this OnlineObject, this is how it receives messages from its "caller"
     */
    protected ObjectInputStream ois;

    /**
     * Public unique ID of this object. This is what it uses to identify itself
     */
    private UUID id;

    /**
     * True if this object is listening to incoming packets
     */
    boolean isListening;

    /**
     * Processor for this object, the processor communicates to this object and tells it what to do
     * when a packet is received
     */
    protected PacketProcessor processor;

    /**
     * ID of the OnlineObject this one is connected to
     */
    protected UUID callerID;

    Thread packetListener;

    /**
     * Creates an OnlineObject with a specified ID
     * @param id UUID to be this OnlineObject's public ID
     */
    public OnlineObject(UUID id){
        setID(id);
        isListening = false;
    }

    public OnlineObject(){
        isListening = false;
    }

    public boolean setID(UUID id){
        if(this.id == null){
            this.id = id;
            return true;
        }
        return false;
    }


    /**
     * Initializes the output and input streams of this object's Socket
     */
    private void initializeStreams() {
        //extract the input and output streams from this socket
        //this is what is used to for I/O

        try {
            Printer.printIfVerbose("Initialized streams.");
            oos = new ObjectOutputStream(s.getOutputStream());
            ois = new ObjectInputStream(s.getInputStream());
        } catch (IOException e) {
            System.out.println("Error while getting streams for connection for OnlineObject");
            System.exit(1);
        }
    }

    /**
     * Initializes the new socket that this object will use to communicate online
     * @param s socket to be used to communicate
     */
    protected void initializeSocket(Socket s){
        this.s = s;
        initializeStreams();
    }



    public UUID getID(){
        return this.id;
    }

    public void startProcessingPackets(){
        startListening();
        processor.start();
    }


    /**
     * This method is called during setup, near the end. It tells the handler to start a thread that
     * begins listening for data coming in from its client. After receiving a packet, it sends it to its server.
     */
    public void startListening(){
        if(isListening) {
            Printer.errorPrintIfVerbose("OnlineObject tried to run the same instance twice");
            return;
        }
        isListening = true;
        Runnable r = () ->
        {
            while(isListening){
                Packet p = waitForPacket();
                if(p!= null) {
                    processor.addPacket(p);
                }
            }
            Printer.printIfVerbose("Listener has stopped");
        };

        packetListener = new Thread(r);
        packetListener.setName("packetListener");
        packetListener.start();
    }


    /**
     * Waits for a  packet to be read from its client, blocks until one is found
     * @return the packet that was eventually read
     */
    protected Packet waitForPacket(){

        try {
            Object data = ois.readObject();
            if(data == null){
                leave();
                return null;
            }
            return decryptPacket(data);
        } catch (IOException | ClassNotFoundException e) {
            return null;
        }


    }

    /**
     * Converts a presumed Packet to the actual packet type
     * @param o the Object that is presumed to be a packet
     * @return o in a Packet form
     */
    private Packet decryptPacket(Object o){
        if(o == null){
            return null;
        }
        if(o instanceof Packet){
            return (Packet)o;
        }
        throw new NotAPacketException("OnlineObject received data that wasn't of type Packet" + o.getClass());
    }

    /**
     * Sends a packet to the caller that this OnlineObject is connected to
     * @param p Packet to go to the caller
     */
    public void sendMessage(Packet p){
        try {
            Printer.debugPrint(Packet.shortenedID(id) + " sent: " + p.toShortenedString());
            oos.writeObject(p);
        } catch(SocketException e){
            //Caller must have terminated
            disconnect();
        }
        catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void setCallerID(UUID id){
        callerID = id;
    }

    public void request(String flag){
        Packet p = new Packet(
                DefaultOnlineCommands.REQUEST + flag,
                null, getID()
        );
        sendMessage(p);
        processor.addRequest(p.getPacketID(), flag);

    }

    public void leave(){
        sendMessage(new Packet(
                DefaultOnlineCommands.QUIT,
                null,
                this.id
        ));
        disconnect();

    }

    public void disconnect(){
        System.out.println("Disconnecting " + Packet.shortenedID(id));
        processor.stop();
        isListening = false;
        try {
            ois.close();
            oos.close();
            packetListener.join();
        } catch (IOException | InterruptedException ignored) {

        }
    }



    protected void onJoin(){
        getInfoFromCaller();
        sendInitialAssignmentsToCaller();
    }

    protected void getInfoFromCaller(){
        request(DefaultOnlineCommands.ID_FLAG);
    }

    protected void sendInitialAssignmentsToCaller(){
    }

    public UUID getCallerID() {
        return callerID;
    }

    public void assignCaller(String flag, Object data){
        Packet p = new Packet(
                DefaultOnlineCommands.ASSIGN + flag,
                data, getID()
        );
        sendMessage(p);
        processor.addRequest(p.getPacketID(), flag);
    }




}
