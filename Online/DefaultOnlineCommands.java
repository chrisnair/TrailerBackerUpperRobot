package Online;

import java.util.UUID;

/**
 * The default commands that the Online package can process
 *
 * @author Joshua Bergthold
 */
public class DefaultOnlineCommands {
    /**
     * Void messages are generally not used, but a typeless message would be sent this way
     */
    public static final String VOID = "v;";
    /**
     * Simple text messages are meant to only contain text and no other commands or data
     */
    public static final String SIMPLE_TEXT = "st;";
    /**
     * Identifier for a request message, where the caller is asking for something about the other
     * This command is proceeded by a flag that indicates what the caller is asking for (requesting)
     */
    public static final String REQUEST = "req;";
    /**
     * Identifier for an answer to a request packet. Packets of this form must contain an answer in some fashion for
     * what the request packet was asking for. This command is proceeded by a flag that indicates what it is sending
     * back,as well as an IDIdentifier that contains the ID of the original request that was saved to ensure that the
     * requester knows what this packet is answering to
     */
    public static final String ANSWER = "ans;";
    /**
     * Flag that is used to communicate that this packet contains or is asking for an ID
     */
    public static final String ID_FLAG = "Iid;";
    /**
     * Identifier to indicate the author is about to disconnect
     */
    public static final String QUIT = "qui;";
    /**
     * Identifier that the sender of this packet requests that the recipient assigns the data of the packet in some way or form.
     */
    public static final String ASSIGN = "ass;";

    public static final String GYRO_READING = "gyr;";

    public static final String INFO = "inf;";

    public static final String CONTROL_SINGAL = "cnt;";

    /**
     * converts a UUID to a IDIdentifier, which is an UUID in the form of a command identifier
     * @param id UUID to be converted
     * @return converted String that contains the UUID
     */
    public static String constructIDIdentifier(UUID id){
        return id.toString()+ ";";
    }

    /**
     * Checks is the given command string is an IDIdentifier
     * @param command String in question
     * @return if the String was an IDIdentifier
     */
    public static boolean isIDIdentifier(String command){
        boolean first = command.charAt(8) == '-';
        boolean second = command.charAt(13) == '-';
        boolean third = command.charAt(18) == '-';
        boolean fourth = command.charAt(23) == '-';
        Printer.debugPrint(command);
        Printer.debugPrint(first + ", " +second + ", " +third + ", " +fourth );
        return  first && second && third && fourth;
    }
}
