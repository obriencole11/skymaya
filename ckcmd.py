""" A python wrapper around ckcmd.exe """


import os
import tempfile
import subprocess


# Local location of ckcmd.exe
CKCMD = os.path.join(os.path.dirname(__file__), 'bin', 'ck-cmd.exe')


def run_command(command, directory='/'):
    """
    Runs a given command in a separate process. Prints the output and raises any exceptions.
    
    Args:
        command(str): A command string to run. 
        directory(str): A directory to run the command in. 
    """
    command = command.replace('\\', '/')
    directory = directory.replace('\\', '/')
    print command
    with open(os.path.join(tempfile.gettempdir(), 'test.log'), 'w') as f:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=directory)
        out, err = process.communicate()
        print out
        if process.returncode != 0 or 'Exception' in err:
            raise CkCmdException('\n%s' % err)


def exportanimation(skeleton_hkx, animation_hkx, output_directory):
    """
    Converts a Skyrim animation from hkx to fbx.
    
    Args:
        skeleton_hkx(str): A skeleton.hkx path. 
        animation_hkx(str): Either an animation hkx file or directory containing animation hkx files.
        output_directory(str): The output directory. 

    Returns:
        str: The executed command string.
    """
    command = '%s exportanimation "%s" "%s" "%s"' % (CKCMD, skeleton_hkx, animation_hkx, output_directory)
    run_command(command, directory=output_directory)
    return command


def importanimation(skeleton_hkx, animation_fbx, output_directory, cache_txt='', behavior_directory=''):
    """
    Converts an animation from fbx to hkx.
    
    Args:
        skeleton_hkx(str): A skeleton.hkx path. 
        animation_fbx(str): An animation fbx file or directory containing animation fbx files. 
        output_directory(str): The output directory. 
        cache_txt(str): An optional cache file to contain root motion data. 
        behavior_directory(str): An optional behavior directory. 

    Returns:
        str: The executed command string.
    """
    command = '%s importanimation "%s" "%s" --c="%s" --b="%s" --e="%s"' % (
        CKCMD, skeleton_hkx, animation_fbx,
        cache_txt, behavior_directory, output_directory
    )
    run_command(command, directory=output_directory)
    return command


def exportrig(skeleton_hkx, skeleton_nif, output_directory,
              animation_hkx='', mesh_nif='', cache_txt='', behavior_directory=''):
    """
    Converts a Skyrim rig from hkx to fbx.
    
    Args:
        skeleton_hkx(str): A skeleton.hkx path. 
        skeleton_nif(str): A skeleton.nif path. 
        output_directory(str): The output directory. 
        animation_hkx(str): Either an animation hkx file or directory containing animation hkx files.
        mesh_nif(str): An optional nif mesh to load or a directory containing mesh nif files. 
        cache_txt(str): An optional cache file to containing root motion data. 
        behavior_directory(str): An optional behavior directory. 

    Returns:
        str: The executed command string.
    """
    commands = [CKCMD, "exportrig"]
    commands.append('"%s"' % skeleton_hkx)
    commands.append('"%s"' % skeleton_nif)
    commands.append('--e="%s"' % output_directory)
    commands.append('--a="%s"' % animation_hkx)
    commands.append('--n="%s"' % mesh_nif)
    commands.append('--b="%s"' % behavior_directory)
    commands.append('--c="%s"' % cache_txt)
    command = ' '.join(commands)
    run_command(command, directory=output_directory)
    return command


def importrig(skeleton_fbx, output_directory):
    """
    Converts a rig from fbx to hkx.
    
    Args:
        skeleton_fbx(str): A skeleton fbx file. 
        output_directory(str): The output directory. 

    Returns:

        str: The executed command string.
    """
    commands = [CKCMD, "importrig"]
    commands.append('"%s"' % skeleton_fbx)
    commands.append('-a "%s"' % '')
    commands.append('-e "%s"' % output_directory)
    command = ' '.join(commands)
    run_command(command, directory=output_directory)
    return command


def importskin(skin_fbx, output_directory):
    """
    Converts a skinned mesh fbx to nif.
    
    Args:
        skin_fbx(str): A skin fbx file. 
        output_directory: 
        output_directory(str): The output directory. 

    Returns:
        str: The executed command string.
    """
    command = '%s importskin "%s" "%s"' % (CKCMD, skin_fbx, output_directory)
    run_command(command, directory=output_directory)
    return command


class CkCmdException(BaseException):
    """ Raised for ckcmd.exe exceptions. """

