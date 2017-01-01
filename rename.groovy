/**
 *  Rename directories given a configurable string transformation
 */

import java.nio.file.*
import java.nio.file.attribute.BasicFileAttributes
import groovy.util.logging.Slf4j
import groovy.transform.ToString

// Logging approach adapted from: 
//   http://stackoverflow.com/questions/15981182/logging-in-groovy-script 
@Grapes([
    @Grab(group='ch.qos.logback', module='logback-classic', version='1.1.8')
])

/** Return a tranformed string given an input string */
interface Xformer {
    String xform(String input)
}

/**
 * Transform a file name created by MacOS Photos to a sortable format
 */
@Slf4j
class MomentToSortable implements Xformer {
    /** Directory exported as "moment" in MacOS Photos app */
    static String MAC_MOMENT_DIR = /(?<location>.*,\s)?(?<date>\w+ \d+, \d+)$/

    String xform(String fname) {
        String newNm = fname.replaceAll(MAC_MOMENT_DIR) { all, location, date ->
            String stamp = Date.parse("MMMM dd, yyyy", date).format("yyyy-MM-dd")
            String rest = location ? location.replaceAll(",", "") : ""
            "${stamp} ${rest}"
        }
    }
}

/**
 * Summary of a renaming job
 */
@ToString(includeNames=true)
class Results {
    int total
    int toRename
    int renamed
    int nonDir
}

/**
 * Rename a directory given a Xformer
 */
@Slf4j
class DirRenamer {

    Xformer xformer 

    def run(String dir, boolean dryRun, boolean verbose=true) {

        if (!xformer) {
            log.error "Xformer not defined"
            return;
        }

        Path path = Paths.get(dir)
        BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes)
        def results = new Results()

        path.eachFile {
            results.total++

            if (!Files.isDirectory(it)) {
                log.warn "Found non-directory: ${it.fileName}" 
                results.nonDir++
                return; // skip to next file
            }
            results.toRename++;
            String newName = xformer.xform("${it.fileName}")

            def parent = new File("${it}").getParent()
            def file = new File(parent + "/" + it.fileName)
            def newFile = new File(parent + "/" + newName)

            if (verbose) {
                log.info "Moving ...\n  FROM: ${file} \n  TO:   ${newFile}\n"
            }

            if (!dryRun) {
                file.renameTo "${newFile}"
                results.renamed++
            }
        }

        log.info "${results}"
    }
}

// -------
//  Main
// -------

def cli = new CliBuilder(usage:'rename')
cli.path(args:1, argName:'path', required:true, 'Path containing directories to rename')
cli.dryRun(argName:'boolean', "Don't rename any files")
def options = cli.parse(args)

if (options) {
    def renamer = new DirRenamer([xformer:new MomentToSortable()])
    renamer.run(options.path, options.dryRun)
}

