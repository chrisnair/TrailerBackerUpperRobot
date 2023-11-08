package Online;

/**
 * This exception is thrown when something goes wrong when processing and executing a Packet
 *
 * @author Joshua Bergthold
 */
public class PacketException extends RuntimeException {
    public PacketException(String s) {
        super(s);
    }
}
