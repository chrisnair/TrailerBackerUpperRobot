package Online;

import java.io.Serializable;
import java.util.UUID;

/**
 *
 * Packets are what the sockets in this program will send to each other
 *
 * @author Joshua Bergthold
 */
public final class Packet implements Serializable {
    /**
     * String that represents what the server should do with the data field
     * command = "{messageType};{dataType};{TBI...}" -> commands = ["messageType;", "dataType;", "TBI...;"]
     */
    private final Command command;


    /**
     * Data to be processed by recipient in some way (often specified by the command)
     */
    private final Object data;

    /**
     * ID of the author of this packet
     */
    private final UUID authorID;

    /**
     * ID of this packet
     */
    private final UUID packetID;




    /**
     * Creates a packet with the specified parameters
     * @param command String that represents what the server should do with the data field
     * @param data data to be processed in some way (often specified by the command)
     * @param authorID id of the author of this packet
     */
     public Packet(String command, Object data, UUID authorID) {
        this(new Command(command), data, authorID);
    }

    /**
     * Creates a packet with the specified parameters
     * @param c Command object that contains a String command
     * @param data data to be processed in some way (often specified by the command)
     * @param authorID id of the author of this packet
     */
    public Packet(Command c, Object data, UUID authorID){
        this.command = c;
        this.authorID = authorID;
        this.packetID = UUID.randomUUID();
        this.data = data;
    }

    /**
     * creates a simple text message with type SIMPLE_TEXT_MESSAGE
     * @param message Text message to be contained in this packet
     * @param authorID id of the author of this packet
     */
    public Packet(String message, UUID authorID){
        this(new Command(DefaultOnlineCommands.SIMPLE_TEXT), message, authorID);
    }







    /**
     * @return the list of commands that this packet holds
     */
    public Command getCommand(){
        return command;
    }

    /**
     * @return data of the packet
     */
    public Object getData() {
        return data;
    }



    /**
     * @return author ID of packet
     */
    public UUID getAuthorID(){
        return this.authorID;
    }

    /**
     * @return ID of this packet
     */
    public UUID getPacketID(){
        return this.packetID;
    }


    @Override
    public String toString(){
        return toShortenedString();
    }

    public String toLongString(){
        return "Packet{PacketID: " + this.packetID + ", Command: " + command.getCommandString() + ", Data: " + this.data +
                ", AuthID: " + this.authorID + ", Type: " + command.getTypeString() + "}";
    }

    /**
     * A short version of the String representation of this packet
     * @return short string version of this packet
     */
    public String toShortenedString(){
        return "Packet{PacketID: " + shortenedID(this.packetID) +
                ", DataType: " + (data != null? this.data.getClass(): "null") +
                ", AuthID: " + shortenedID(this.authorID) +
                ", Type: " + command.getTypeString() + "}";
    }

    /**
     * Shortened author ID of this packet
     * @return shortened ID
     */
    public String shortAuthID(){
        return shortenedID(authorID);
    }

    /**
     * @return The type of this packet
     */
    public String getType(){
        if(command == null){
            return "null";
        }
        return command.getType();
    }

    /**
     * Helper method that takes a UUID and returns a shortened version of it
     * @param id full iD
     * @return String version of the shortened ID
     */
    public static String shortenedID(UUID id){
        if(id == null){
            return "null";
        }
        String str = id.toString();
        return str.substring(str.length()-12);
    }
}
