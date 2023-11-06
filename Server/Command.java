package Online;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.UUID;

/**
 * Commands are used to encode the action that a packet intends.
 *
 * @author Joshua Bergthold
 */
public final class Command implements Serializable {


    /**
     * List that represents the source string of this command. Encodes the action of this command.
     * command = "{messageType};{dataType};{TBI...}" -> commands = ["messageType;", "extraInfo;", ... ]
     */
    private final List<String> commands;

    /**
     * Creates a command object that carries the given command's data
     * @param command String that contains the command symbols (Using DefaultOnlineCommands by default)
     */
    public Command(String command){
        commands = parseCommand(command);
    }

    /**
     * Parser that converts a command string to an ArrayList of commands
     * @param command raw command to be parsed
     * @return parsed command in ArrayList form
     */
    private ArrayList<String> parseCommand(String command){
        int start = 0;

        ArrayList<String> result = new ArrayList<>();
        for(int i = 0; i < command.length(); i++){
            if(command.charAt(i) == ';') {
                i++;
                result.add(command.substring(start,i));
                start = i;
            }
        }
        return result;
    }

    /**
     * @return the command unpacked into a string form
     */
    public String getCommandString(){
        StringBuilder result = new StringBuilder();
        for(String cmd: commands){
            result.append(cmd);
        }
        return result.toString();
    }

    /**
     * Converts the type of this message (given in the commands) to a readable string and returns it
     * @return the readable representation of the type
     */
    public String getTypeString(){
        switch(getType()){
            case DefaultOnlineCommands.SIMPLE_TEXT -> {
                return "simpleTextMessage";
            }
            case DefaultOnlineCommands.VOID -> {
                return "voidMessage";
            }
            case DefaultOnlineCommands.REQUEST -> {
                return "request " + getCommandLine(1);
            }
            case DefaultOnlineCommands.ANSWER -> {
                return "answer " + getCommandLine(1);
            }
            case DefaultOnlineCommands.INFO -> {
                return "info " + getCommandLine(1);
            }
            case DefaultOnlineCommands.CONTROL_SIGNAL -> {
                return "control signal " + getCommandLine(1);
            }
            case DefaultOnlineCommands.QUIT -> {
                return "quit";
            }
            default -> {
                return getType() + " (Non-default or unknown)";
            }
        }

    }

    /**
     * the command's "type" is the first symbol in its command
     * @return type of command
     */
    public String getType() {
        return commands.get(0);
    }

    /**
     * Returns a certain line (symbol) form this command's list of symbols
     * @param index which symbol to get
     * @return the selected symbol
     */
    public String getCommandLine(int index){
        if(commands.size() <= index){
            return "-";
        }
        return commands.get(index);
    }

    /**
     * Simply removes the semicolon that is at the end of each command
     * @param command command, in string form, to be modified
     * @return the truncated command
     */
    public static UUID extractIDFromCommandLine(String command){
        if(command.equals("-")) return null;
        return UUID.fromString(command.substring(0, command.length()-1));
    }
}
