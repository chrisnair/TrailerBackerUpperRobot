package Online;

/**
 * This is a runtime exception that is thrown when something receives data
 * that was presumed to be a Packet, but wasn't
 *
 * @author Joshua Bergthold
 */
public class NotAPacketException extends RuntimeException{
    public NotAPacketException(String m){
        super(m);
    }
    public NotAPacketException(){
        super();
    }
}
