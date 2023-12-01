package Online;

import java.util.*;

/**
 * A PacketProcessor is used to decode packets and call methods of its Host
 * based on those packet commands
 *
 * @author Joshua Bergthold
 */
public class PacketProcessor {
    /**
     * List of Packets that are queued to be executed by the server
     * NOTE: volatile is very important because the queue is being concurrently
     * modified on multiple threads
     * so if we keep queue in a register, the other threads won't see the changes to
     * their local "copy"
     * So the volatile keyword keeps the packets variable in memory instead of the
     * CPU registers
     */
    private volatile Queue<Packet> packets;

    /**
     * These keep track of what requests are out. Keeps track of the "request IDs"
     * and
     * what that request was asking for that an answer packet must show to know that
     * a
     * request was fulfilled correctly. Useful when multiple requests are sent out,
     * or
     * an answer packet was sent in vain. We don't want a client to be able to send
     * an
     * answer packet and an arbitrary time and the server carries out that packet. A
     * server should only accept information it asks for
     */
    private final Map<UUID, String> requestsOut;

    /**
     * The host is what this packet processor reports to. The purpose of the packet
     * processor is to decode information and make changes to its host
     */
    protected OnlineObject host;

    /**
     * True if this packet processor is actively listening to and processing packets
     */
    private boolean running;

    /**
     * The thread that listens for new packets that the host gives it, and is
     * running
     * when the processor is actively processing packets
     */
    private Thread processorThread;

    /**
     * Creates a packet processor that reports to a host
     * 
     * @param host host that this processor makes changes to
     */
    public PacketProcessor(OnlineObject host) {
        packets = new LinkedList<>();
        requestsOut = new HashMap<>();
        this.host = host;
    }

    /**
     * Called by other classes to add a packet to the Server
     * 
     * @param p data to be received
     */
    public void addPacket(Packet p) {
        if (p == null)
            return;
        packets.add(p);
    }

    /**
     * Adds a request to this PacketProcessor object
     * 
     * @param requestID ID of the request
     */
    public void addRequest(UUID requestID, String flag) {
        requestsOut.put(requestID, flag);
    }

    /**
     * Starts this PacketProcessor, meaning it starts actively listening for packets
     * and executes them
     */
    public void start() {
        if (running) {
            return;
        }
        running = true;
        startProcessingPackets();
    }

    /**
     * Starts a thread that executes the active Packets located in the list of
     * packets
     */
    private void startProcessingPackets() {
        Runnable packetProcessor = () -> {
            // Printer.printIfVerbose("Starting processing packets");
            while (running) {
                if (!packets.isEmpty()) {
                    // Printer.debugPrint("Packet queue= " + packets.size());
                    Packet p = packets.poll();
                    try {
                        if (p == null)
                            continue;
                        // Printer.printIfVerbose("Executing: " + p);
                        executePacket(p);
                    } catch (InvalidCommandException e) {
                        e.printStackTrace();
                    }
                }

                try {
                    Thread.sleep(1000 / 60);
                } catch (InterruptedException e) {
                    // TODO Auto-generated catch block
                    e.printStackTrace();
                }

            }

        };

        processorThread = new Thread(packetProcessor);
        processorThread.setName("Packet Processor for " + host.getID());
        processorThread.start();
    }

    /**
     * Executes the action encoded in the packet, if the child class hasn't
     * implemented the execution of a packet type,
     * it uses the default PacketProcessor functionalities
     *
     * Override this method to add new types of packets that can be processed
     * 
     * @param p Packet with the command to be executed.
     */
    public void executePacket(Packet p) {
        System.out.println("Packet recieved!");
        // Printer.debugPrint("PacketProcessor level: " + p.toLongString());

        switch (p.getType()) {
            case DefaultOnlineCommands.REQUEST:
                processRequestPacket(p);
                return;

            case DefaultOnlineCommands.ANSWER:
                checkAndProcessAnswerPacket(p);
                return;

            case DefaultOnlineCommands.QUIT:
                // Printer.printIfVerbose(p.shortAuthID() + " has left.");
                host.leave();
                return;

            case DefaultOnlineCommands.ASSIGN:
                processAssignPacket(p);
                return;

            default:
                // Printer.printIfVerbose("Packet type not supported: " +
                // p.toShortenedString());
        }

    }

    protected void processAssignPacket(Packet p) {
        switch (p.getCommand().getCommandLine(1)) {
            case DefaultOnlineCommands.ID_FLAG:
                // Printer.debugPrint("ID assignment received, assigning to: " + p.getData());
                host.setID((UUID) p.getData());
                return;
        }
    }

    /**
     * Defines what this processor should do with a request packet
     *
     * This method needs to be overridden if you want to process new types of
     * requests
     * 
     * @param p packet that contains the request
     */
    protected void processRequestPacket(Packet p) {
        switch (p.getCommand().getCommandLine(1)) {
            case DefaultOnlineCommands.ID_FLAG:
                sendIDAnswerPacket(p);
                return;
        }
    }

    /**
     * Helper method that constructs and sends an answer packet based on the given
     * params
     * 
     * @param requester the packet that requested the information (Its requestID and
     *                  request type will be extracted)
     * @param data      data that serves as the response to the request
     */
    protected void sendAnswerPacket(Packet requester, Object data) {
        String command = DefaultOnlineCommands.ANSWER + requester.getCommand().getCommandLine(1)
                + DefaultOnlineCommands.constructIDIdentifier(requester.getPacketID());
        host.sendMessage(new Packet(command, data, host.getID()));
    }

    /**
     * Sends an answer packet that contains the host's id
     * 
     * @param p request packet that this is being answered
     */
    private void sendIDAnswerPacket(Packet p) {
        sendAnswerPacket(p, null);
    }

    /**
     * Checks is this answer packet is an answer to a request that is out. If it is,
     * then it
     * processes the answer packet by calling processAnswerPacket()
     * 
     * @param p packet to be checked and executed
     */
    private void checkAndProcessAnswerPacket(Packet p) {
        UUID packetRequestID = Command.extractIDFromCommandLine(p.getCommand().getCommandLine(2));
        boolean requestIsOut = requestsOut.containsKey(packetRequestID);

        String packetRequestType = p.getCommand().getCommandLine(1);
        String processorRequestType = requestsOut.get(packetRequestID);
        boolean requestIsCorrectType = packetRequestType.equals(processorRequestType);
        if (!requestIsOut || !requestIsCorrectType) {
            // Printer.errorPrintIfVerbose("Answer packet wasn't being tracked correctly, or
            // answer was sent in vain");
            // Printer.errorPrintIfVerbose("requestIsOut = "+ requestIsOut +
            // "\nrequestIsCorrectType = "+ requestIsCorrectType);
            // Printer.errorPrintIfVerbose(packetRequestType + " ?= " +
            // processorRequestType);
            return;
        }
        // Printer.debugPrint("Answer packet passed checks");
        requestsOut.remove(packetRequestID);
        processAnswerPacket(p);
    }

    /**
     * Processes an answer packet, by this point, it has already been checked that
     * it is a
     * valid answer to a request that was out
     * 
     * @param p
     */
    protected void processAnswerPacket(Packet p) {
        switch (p.getCommand().getCommandLine(1)) {
            case DefaultOnlineCommands.ID_FLAG:
                host.setCallerID(p.getAuthorID());
                return;
            default:
                // Printer.errorPrintIfVerbose("Unimplemented request type: "+
                // p.getCommand().getCommandLine(1));

        }

    }

    /**
     * Stops the listening and execution of packets
     */
    public void stop() {
        this.running = false;
        processorThread.interrupt();
    }

    /**
     * @return the host of this packet processor
     */
    public OnlineObject getHost() {
        return host;
    }

}
