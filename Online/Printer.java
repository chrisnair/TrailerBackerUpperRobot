package Online;

/**
 * Simple debugging tool that prints something if the verbose flag is true <br>
 * We do NOT use logger :)
 *
 * @author Joshua Bergthold
 */
public class Printer {
    private static boolean verbose = true;
    private static boolean debug = true;

    /**
     * Prints the Object if the verbose flag is on
     * @param o Object to be printed
     */
    public static void printIfVerbose(Object o){
        if(verbose){
            System.out.println("\u001b[33m" + o + "\u001b[0m");
        }
    }

    /**
     * Print something with red text highlighting if the verbose flag is on
     * @param o Object to be printed
     */
    public static void errorPrintIfVerbose(Object o){
        if(verbose){
            System.out.println(" \u001b[31m" + o + "\u001b[0m");
        }
    }

    /**
     * Prints something with its own special green color when the debug flag is on
     * @param o Object to be printed
     */
    public static void debugPrint(Object o){
        if(debug) {
            System.out.println("\u001b[32m" + o + "\u001b[0m");
        }
    }

    /**
     * @return true if the verbose flag is on
     */
    public static boolean isVerbose(){
        return verbose;
    }

    /**
     * If verbose is currently true, this method makes it false, same with false -> true
     */
    public static void toggleVerbosity(){
        verbose = !verbose;
    }

    /**
     * Minecraft F3 hehe
     */
    public static void toggleDebugosity(){
        debug = !debug;
    }
}
