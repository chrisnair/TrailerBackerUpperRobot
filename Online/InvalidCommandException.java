package Online;

/**
 * InvalidCommandException is thrown when a command in a packet is not recognized,
 * and the server cannot do anything with the packet
 *
 * @author Joshua Bergthold
 */
public class InvalidCommandException extends RuntimeException{
    public InvalidCommandException(String m){
        super("Command: \"" + m + "\" is not valid");
    }
}
