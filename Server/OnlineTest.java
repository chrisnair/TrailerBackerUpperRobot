package Online;

import org.junit.Test;

import java.awt.*;
import java.util.ArrayList;
import java.util.UUID;

import static org.junit.Assert.*;

public class OnlineTest {

    @Test
    public void packetCommandTest(){
        /*
        String expectedCommandString = "s;as;er;";
        ArrayList<String> expectedCommands = new ArrayList<>();
        expectedCommands.add("s;");
        expectedCommands.add("as;");
        expectedCommands.add("er;");

        Packet p = new Packet(expectedCommandString, null, null);

        assertEquals(expectedCommandString, p.getCommandString());
        assertEquals(expectedCommands, p.getCommands());

         */
    }

    @Test
    public void DefaultOnlineCommandsTest(){
        for(int i = 0; i < 10 ; i++) {
            UUID test = UUID.randomUUID();
            assertTrue(DefaultOnlineCommands.isIDIdentifier(test.toString()));
        }

        UUID test = UUID.randomUUID();
        assertFalse(DefaultOnlineCommands.isIDIdentifier("4"+test.toString()));

    }



}
