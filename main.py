"""
Main functions for using ckcmd in Maya.
"""


import os
import shutil

import pymel.core as pmc

from pywind_old import maya as om2
from skymaya import ckcmd

ROOT_NAME = 'NPC_s_Root_s__ob_Root_cb_'
BOUNDING_BOX_NAME = 'BoundingBox'
MATCH_ATTR_NAME = 'retargetMatch'
RETARGET_ATTR_NAME = 'retargetAnimMatch'
RIG_NAMESPACE = 'RIG'
SCENE_DIRECTORY = None


def getSceneDirectory():
    """ 
    Gets the current directory of the open scene. 
    If the current scene is new the user will be prompted to select a directory.
    """
    global SCENE_DIRECTORY
    sceneName = pmc.sceneName()
    if sceneName != '' and sceneName is not None:
        return os.path.dirname(pmc.sceneName())
    elif SCENE_DIRECTORY is not None:
        return SCENE_DIRECTORY
    else:
        directories = pmc.fileDialog2(dialogStyle=1, caption='Select Project Directory', fileMode=2) or []
        if len(directories) == 0:
            raise FilePathException('No directory selected.')
        SCENE_DIRECTORY = directories[0]
        return SCENE_DIRECTORY


def getParentDirectory(path):
    """ Returns the parent directory of the given directory. """
    return os.path.abspath(os.path.join(path, os.pardir))


def saveFbxDialog(title='Save Fbx Dialog', dir=None):
    """
    Opens a file dialog prompting the user to save an fbx file. 

    Returns:
        str: The output fbx file path.
    """
    filepaths = pmc.fileDialog2(fileFilter='*.fbx', dialogStyle=1, caption=title, dir=dir or getSceneDirectory(),
                                fileMode=0) or []
    if len(filepaths) == 0:
        raise FilePathException('No file path selected.')
    return filepaths[0]


def loadFbxDialog(title='Load Fbx Dialog', dir=None):
    """
    Opens a file dialog prompting the user to load an fbx file.

    Returns:
        str: The selected fbx file path.
    """
    filepaths = pmc.fileDialog2(fileFilter='*.fbx', dialogStyle=1, caption=title, dir=dir or getSceneDirectory(),
                                fileMode=1) or []
    if len(filepaths) == 0:
        raise FilePathException('No file path selected.')
    return filepaths[0]


def loadFbxsDialog(title='Load Fbxs Dialog', dir=None):
    """
    Opens a file dialog prompting the user to load fbx files.

    Returns:
        list: A list of selected fbx files.
    """
    filepaths = pmc.fileDialog2(fileFilter='*.fbx', dialogStyle=1, caption=title, dir=dir or getSceneDirectory(),
                                fileMode=4) or []
    if len(filepaths) == 0:
        raise FilePathException('No file paths selected.')
    return filepaths


def loadSceneDialog(title='Load Scene Dialog', dir=None):
    """
    Opens a file dialog prompting the user to load an maya scene.

    Returns:
        str: The selected maya file path.
    """
    filepaths = pmc.fileDialog2(fileFilter='*.ma', dialogStyle=1, caption=title, dir=dir or getSceneDirectory(),
                                fileMode=1) or []
    if len(filepaths) == 0:
        raise FilePathException('No file path selected.')
    return filepaths[0]


def loadScenesDialog(title='Load Scenes Dialog', dir=None):
    """
    Opens a file dialog prompting the user to load maya scenes.

    Returns:
        list: The selected maya file paths.
    """
    filepaths = pmc.fileDialog2(fileFilter='*.ma', dialogStyle=1, caption=title, dir=dir or getSceneDirectory(),
                                fileMode=4) or []
    if len(filepaths) == 0:
        raise FilePathException('No file paths selected.')
    return filepaths


def getDirectoryDialog(title='Get Directory'):
    """
    Opens a file dialog prompting the user to get an directory.

    Returns:
        str: The selected directory path.
    """
    directories = pmc.fileDialog2(dialogStyle=1, caption=title, dir=getSceneDirectory(),
                                fileMode=2) or []
    if len(directories) == 0:
        raise FilePathException('No directory selected.')
    return directories[0]


def saveScenePrompt():
    """
    Prompts the user to save the scene or cancel the operation.
    
    Returns:
        bool: True if the scene should be saved, False if it shouldn't.
    """
    result = pmc.confirmDialog(
        title='Save Scene Dialog',
        message='Save changes to %s?' % pmc.sceneName(),
        button=['Save', "Don't Save", 'Cancel'], defaultButton='Cancel', cancelButton='Cancel', dismissString='Cancel')
    if result == 'Cancel':
        raise SaveSceneException('Cancelled operation.')
    return result == 'Save'


def getDataDirectory(path):
    """
    Attempts to find a root data directory containing the given directory.
    
    Args:
        path(str): A directory path. 

    Returns:
        A root directory path.
    """

    # Attempt to find a root based on consistant folder names.
    if path.endswith('meshes') or path.endswith('textures'):
        return getParentDirectory(path)
    elif path.endswith('actors'):
        parentDir = getParentDirectory(path)
        if parentDir.endswith('meshes') or parentDir.endswith('textures'):
            return getParentDirectory(parentDir)

    # Check if the path itself is a root directory
    children = os.listdir(path)
    if 'meshes' in children or 'textures' in children:
        if 'actors' in os.listdir(os.path.join(path, 'meshes')):
            return path

    # If the path has no parent, raise an exception
    if getParentDirectory(path) == path:
        raise DirectoryException

    try:
        return getDataDirectory(getParentDirectory(path))
    except DirectoryException:
        # In case of root exception error, catch it and raise the exception for the original path
        raise DirectoryException('Could not find data root for path "%s"' % path)


def getSceneDataDirectory():
    """ Gets the skyrim data root directory for the current scene. """
    return getDataDirectory(getSceneDirectory())


def getActor(path):
    """
    Finds a creature project name for the given path.
    
    Args:
        path(str): A directory path.

    Returns:
        str: A skyrim creature name.
    """
    parent = getParentDirectory(path)
    if parent == path:
        return None

    parentName = os.path.basename(parent)
    if 'dlc' in parentName or 'actors' in parentName:
        return os.path.basename(path)

    return getActor(parent)


def getSceneActor():
    """ Gets a actor name for the current scene. """
    return getActor(getSceneDirectory())


def getDlc(path):
    """
    Returns the dlc number for the given path. If this is a vanilla path None will be returned.
    
    Args:
        path(str): A directory path.

    Returns:
        int: A dlc number or None.
    """
    baseName = os.path.basename(path)
    if 'dlc' in baseName:
        return int(path[-1])
    if getParentDirectory(path) == path:
        return None
    return getDlc(getParentDirectory(path))


def getSceneDlc():
    """ Gets a dlc number for the current scene. """
    return getDlc(getSceneDirectory())


def getSubDirectory(root, subdirectories):
    """
    Attempts to find a valid path matching the input directory pattern. 
    A subdirectory value of None designates any sub directory, a list will try each option.
    This is used to find directories matching Skyrims data structure.
    
    Args:
        root(str): The root directory to search. 
        subdirectories(list): A list of sub-directory names. 

    Returns:
        str: The directory path if found or None.
    """
    if len(subdirectories) == 0:
        return root

    try:
        next_dir = subdirectories[0]
        if next_dir is None:
            for root, dirs, files in os.walk(root):
                next_dir = dirs + files
                next_dir = next_dir[0]
                return getSubDirectory(os.path.join(root, next_dir), subdirectories[1:])
            raise DirectoryException
        elif isinstance(next_dir, (list, tuple)):
            for dir in next_dir:
                subdirectory = os.path.join(root, dir)
                if not os.path.isdir(subdirectory):
                    continue
                subdirectory = getSubDirectory(subdirectory, subdirectories[1:])
                if subdirectory:
                    return subdirectory
            raise DirectoryException
        else:
            subdirectory = os.path.join(root, next_dir)
            if not os.path.isdir(subdirectory):
                raise DirectoryException
            return getSubDirectory(subdirectory, subdirectories[1:])
    except DirectoryException:
        paths = [root] + [str(directory) for directory in subdirectories]
        raise DirectoryException('Could not find sub directory "%s"' % os.path.join(*paths))


def getSubFile(root, keyword):
    """
    Finds a file in the given directory containing the given keyword.
    
    Args:
        root(str): A root path to search. 
        keyword(str): A keyword to search for.

    Returns:
        str: A file path or None.
    """
    if root is None:
        return None
    for root, dirs, files in os.walk(root):
        if keyword is None:
            return os.path.join(root, files[0])
        for file in files:
            if keyword in file:
                return os.path.join(root, file)
    return None


def getTextureDirectory(root, actor=None, dlc=None):
    """
    Gets a texture directory within the given root.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 
        
    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['textures', 'actors', actor]
    if dlc:
        subdirectories.insert(1, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneTextureDirectory():
    return getTextureDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getAnimationDirectory(root=None, actor=None, dlc=None):
    """
    Finds a animation directory within the given root.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors', actor, 'animations']
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneAnimationDirectory():
    return getAnimationDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getCharacterAssetDirectory(root, actor=None, dlc=None):
    """
    Finds a character assets directory within the given root.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors', actor, ['character assets', 'characterassets']]
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneCharacterAssetDirectory():
    return getCharacterAssetDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getBehaviorDirectory(root, actor=None, dlc=None):
    """
    Finds a character assets directory within the given root.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors', actor, 'behaviors']
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneBehaviorDirectory():
    return getBehaviorDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getAnimationDataDirectory(root):
    """
    Finds an animation data directory within the given root.
    
    Args:
        root(str): A root path to search.

    Returns:
        str: The directory if found, otherwise None.
    """
    return getSubDirectory(root, ['meshes', 'animationdata'])


def getCacheFile(root, name):
    """
    Finds an animation cache file containing the given name.
    
    Args:
        root(str): A root path to search.
        name(str): A keyword contained in the cache file name. 

    Returns:
        str: The file path if found, otherwise None.
    """
    return getSubFile(getAnimationDataDirectory(root), name)


def getBoundAnimDirectory(root):
    """
    Finds a bound anim data directory within the given root.
    
    Args:
        root(str): A root path to search.

    Returns:
        str: The directory if found, otherwise None.
    """
    return getSubDirectory(root, ['meshes', 'animationdata', 'boundanims'])


def getBoundAnimFile(root, name):
    """
    Finds an animation bound anim file containing the given name.
    
    Args:
        root(str): A root path to search.
        name(str): A keyword contained in the cache file name. 

    Returns:
        str: The file path if found, otherwise None.
    """
    return getSubFile(getBoundAnimDirectory(root), name)


def getSceneCacheFile():
    return getCacheFile(getSceneDataDirectory(), getSceneActor())


def getTagDirectory(root, actor=None, dlc=None):
    """
    Finds an animation tag directory within the given root.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors', actor, 'tags']
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneTagDirectory():
    return getTagDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getActorDirectory(root, actor=None, dlc=None):
    """
    Finds an actor directory within the given root.

    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors', actor]
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def getSceneActorDirectory():
    return getActorDirectory(getSceneDataDirectory(), getSceneActor(), getSceneDlc())


def getActorsDirectory(root, dlc=None):
    """
    Finds an actors directory within the given root.

    Args:
        root(str): A root path to search.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The directory if found, otherwise None.
    """
    subdirectories = ['meshes', 'actors']
    if dlc:
        subdirectories.insert(2, 'dlc0%s' % dlc)
    return getSubDirectory(root, subdirectories)


def listActors(root, dlc=None):
    """
    Lists all actors in the given data directory for the given dlc.
    
    Args:
        root(str): A root path to search.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        list: A list of actor names.
    """
    return os.listdir(getActorsDirectory(root, dlc=dlc))


def getSkeletonHkx(root, actor=None, dlc=None, legacy=False):
    """
    Gets a skeleton.hkx file for the given root directory.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 
        legacy(bool): Whether to return a legacy skeleton.

    Returns:
        str: The file path if found, otherwise None.
    """
    return getSubFile(getCharacterAssetDirectory(root, actor, dlc=dlc), 'skeleton_le.hkx' if legacy else 'skeleton.hkx')


def getSceneSkeletonHkx(legacy=False):
    root, actor, dlc = getSceneDataDirectory(), getSceneActor(), getSceneDlc()
    return getSkeletonHkx(root, actor, dlc, legacy=legacy)


def getSkeletonNif(root, actor=None, dlc=None):
    """
    Gets a skeleton.nif file for the given root directory.
    
    Args:
        root(str): A root path to search.
        actor(str): An optional actor name. Default will return the first one found.
        dlc(int): An optional dlc number, default will search for a vanilla project. 

    Returns:
        str: The file path if found, otherwise None.
    """
    return getSubFile(getCharacterAssetDirectory(root, actor, dlc=dlc), 'skeleton.nif')


def getSceneSkeletonNif():
    root, actor, dlc = getSceneDataDirectory(), getSceneActor(), getSceneDlc()
    return getSkeletonNif(root, actor, dlc)


class ProgressContext(object):
    """ A progress bar context manager. """
    def __init__(self, count=1, title='Progress Bar'):
        self.count = count
        self.title = title
        self.bar = pmc.mel.eval('$tmp = $gMainProgressBar');

    def __enter__(self):
        pmc.progressBar(self.bar, edit=True, beginProgress=True, isInterruptable=False, maxValue=self.count)
        return self

    def setStatus(self, status):
        pmc.progressBar(self.bar, edit=True, status=status)

    def step(self):
        pmc.progressBar(self.bar, edit=True, step=1)

    def __exit__(self, *args, **kwargs):
        pmc.progressBar(self.bar, edit=True, endProgress=True)


def extractActor(path=None, actor=None, destination=None):
    """
    Extracts an actors files to a separate directory.
    
    Args:
        path(str): A source data directory or actor directory. 
        actor(str): An actor name. 
        destination(str): An output data directory. 

    Returns:
        str: The destination directory.
    """
    path = path or getDirectoryDialog('Source Directory')
    srcRoot = getDataDirectory(path)
    actor = actor or getActor(path) or getDirectoryDialog('Actor Directory')
    dstRoot = destination or getDirectoryDialog('Destination Directory')
    dlc = getDlc(path)
    srcActorDir = getActorDirectory(srcRoot, actor, dlc)
    srcTextureDir = getTextureDirectory(srcRoot, actor, dlc)
    srcCacheFile = getCacheFile(srcRoot, actor)
    srcBoundAnimFile = getBoundAnimFile(srcRoot, actor)

    def makeDir(path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def copyDir(src, dst):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks=False, ignore=None)
            else:
                shutil.copy2(s, d)

    # Make core directories
    meshDir = makeDir(os.path.join(dstRoot, 'meshes'))
    actorsDir = makeDir(os.path.join(meshDir, 'actors'))
    actorDir = makeDir(os.path.join(actorsDir, actor))
    textureDir = makeDir(os.path.join(dstRoot, 'textures'))
    texturesDir = makeDir(os.path.join(textureDir, 'actors'))
    textureDir = makeDir(os.path.join(texturesDir, actor))
    animDataDir = makeDir(os.path.join(meshDir, 'animationdata'))
    boundAnimDir = makeDir(os.path.join(animDataDir, 'boundanims'))

    # Copy actor directories
    copyDir(srcActorDir, actorDir)
    copyDir(srcTextureDir, textureDir)
    if srcCacheFile is not None:
        shutil.copyfile(srcCacheFile, os.path.join(animDataDir, os.path.basename(srcCacheFile)))
    if srcBoundAnimFile is not None:
        shutil.copyfile(srcBoundAnimFile, os.path.join(boundAnimDir, os.path.basename(srcBoundAnimFile)))

    # Copy Data Set Files
    srcMeshDir = os.path.join(srcRoot, 'meshes')
    for filename in os.listdir(meshDir):
        if filename.endswith('.txt'):
            shutil.copyfile(os.path.join(srcMeshDir, filename), os.path.join(meshDir, filename))


def convertDataDirectory(path=None):
    """
    Converts an entire data directory from skyrim formats to fbx. 
    
    Args:
        path(str): A path to convert. 
    """
    path = path or getDirectoryDialog('Get Data Directory')
    root = getDataDirectory(path)

    for dlc in [None, 1, 2]:
        try:
            actors = listActors(root, dlc)
        except DirectoryException:
            continue

        with ProgressContext(count=len(actors) * 2) as progress:
            for actor in actors:
                skeletonHkx = getSkeletonHkx(root, actor, dlc)
                skeletonNif = getSkeletonNif(root, actor, dlc)
                characterAssetsDir = getCharacterAssetDirectory(root, actor, dlc)
                animationDir = getAnimationDirectory(root, actor, dlc)
                cacheFile = getCacheFile(root, actor)
                behaviorDir = getBehaviorDirectory(root, actor, dlc)

                # Export rig and animations
                progress.setStatus('Exporting %s rig' % actor)
                ckcmd.exportrig(skeletonHkx, skeletonNif, characterAssetsDir,
                                animation_hkx=animationDir, cache_txt=cacheFile, behavior_directory=behaviorDir)
                progress.step()

                # Export tags
                try:
                    tagDir = getTagDirectory(root, actor, dlc)
                except DirectoryException:
                    tagDir = os.path.join(getActorDirectory(root, actor, dlc), 'tags')
                    os.makedirs(tagDir)
                progress.setStatus('Exporting %s animations' % actor)
                ckcmd.exportanimation(skeletonHkx, animationDir, tagDir)
                progress.step()


def getRootJoint(namespace=None):
    """
    Finds a root joint in the scene.
    
    Returns:
        PyNode: A root joint if found.
    """
    name = ROOT_NAME if namespace is None else '%s:%s' % (namespace, ROOT_NAME)
    if pmc.objExists(name):
        return pmc.PyNode(name)
    return None


def getBoundingBox(namespace=None):
    """
    Finds a bounding box in the scene.
    
    Returns:
        PyNode: A box node if found.
    """
    name = BOUNDING_BOX_NAME if namespace is None else '%s:%s' % (namespace, BOUNDING_BOX_NAME)
    if pmc.objExists(name):
        return pmc.PyNode(name)
    return None


def getRootSkeleton():
    """ Finds an entire export skeleton. """
    root = getRootJoint()
    if root is None:
        raise RootJointException('Failed to find root skeleton.')

    return [root] + [joint for joint in root.listRelatives(ad=True, type='joint') if not joint.name().endswith('_rb')]


def getBindSkeleton():
    """ Finds the skin-friendly joints of an export skeleton. """
    root = getRootJoint()
    if root is None:
        raise RootJointException('Failed to find root skeleton.')

    joints = [joint for joint in root.listRelatives(ad=True, type='joint') if not joint.name().endswith('_rb')]
    joints = [joint for joint in joints if 'Camera01' not in joint.name()]
    joints = [joint for joint in joints if 'MagicEffectsNode' not in joint.name()]
    return joints


def getMeshes(nodes=None):
    """ Gets all mesh nodes from the given nodes."""
    meshes = []
    nodes = nodes if nodes is not None else pmc.selected()
    for node in nodes:
        if node.nodeType() == 'mesh':
            meshes.append(node)
        else:
            meshes.extend(node.listRelatives(type='mesh'))
    return [mesh for mesh in meshes if 'Orig' not in mesh.name()]


def importFbx(path=None, update=False, dir=None):
    """
    Imports the given fbx file.

    Args:
        path(str): An fbx file path. 
        update(bool): Whether to update scene nodes instead of adding. 
        dir(str): An optional directory to start in.

    Returns:
        list: A list of imported nodes.
    """
    path = path or loadFbxDialog(dir=dir)

    if not str(path).endswith('.fbx'):
        raise FbxException('"%s" is not an fbx file.' % path)
    if not os.path.exists(path):
        raise FbxException('Path "%s" does not exist' % path)

    mObjects = []

    def addNode(mObject, *args):
        """ A function that stores all added nodes. """
        mObjects.append(mObject)

    # Create a callback to listen for new nodes.
    callback = om2.MDGMessage.addNodeAddedCallback(addNode, 'dependNode')
    try:
        # Import the file
        pmc.unloadPlugin('fbxmaya')
        pmc.loadPlugin('fbxmaya')
        pmc.mel.eval('FBXImportMode -v %s' % ('exmerge' if update else 'add'))
        pmc.mel.eval('FBXImport -f "%s"' % path.replace('\\', '/'))
    finally:
        # Always remove the callback
        om2.MMessage.removeCallback(callback)

    # Convert mObjects to node names
    nodes = set()
    for mObject in mObjects:
        if mObject.isNull():
            continue
        if mObject.hasFn(om2.MFn.kDagNode):
            name = om2.MFnDagNode(mObject).fullPathName()
        else:
            name = om2.MFnDependencyNode(mObject).name()
        if pmc.objExists(name):
            nodes.add(pmc.PyNode(name))

    return list(nodes)


def _checkMaxInfluences(mesh, max=4):
    """
    Checks if the given mesh has more influences per-vertex than a given maximum.
    
    Args:
        mesh(PyNode): A mesh node.
        max(int): The max influences to check for.

    Returns:
        bool: Whether the mesh has more influences than the maximum.
    """
    mesh = pmc.PyNode(mesh)
    vertices = mesh.getVertices()[1]
    clusters = pmc.ls(pmc.listHistory(mesh), type='skinCluster') or []
    if len(clusters) == 0:
        return True
    cluster = clusters[0]

    for vert in vertices:
        joints = pmc.skinPercent(cluster, '%s.vtx[%s]' % (mesh, vert),
                                 query=True, ignoreBelow=0.000001, transform=None) or []
        if len(joints) > max:
            return False
    return True


def exportFbx(nodes=None, path=None, animation=False):
    """
    Exports the given nodes as an fbx file.
    
    Args:
        nodes(list): A list of nodes to export. If None the current selection will be used. 
        path(str): The destination fbx file path. If None a dialog will prompt the user to select one. 
        animation(bool): Whether to optimize for animation export.

    Returns:
        str: The fbx file path.
    """
    path = path or saveFbxDialog()

    # Determine what nodes we're exporting
    nodes = [pmc.PyNode(node) for node in nodes] if nodes is not None else pmc.selected()
    nodes = [node for node in nodes if 'shape' not in pmc.nodeType(node, i=True)]

    try:
        pmc.undoInfo(openChunk=True)

        # Export and restore the original selection
        pmc.select(nodes)
        pmc.mel.eval('FBXExportEmbeddedTextures -v false')
        pmc.mel.eval('FBXExportShapes -v true' if not animation else 'FBXExportShapes -v false')
        pmc.mel.eval('FBXExportSkins -v true' if not animation else 'FBXExportSkins -v false')
        pmc.mel.eval('FBXExportTriangulate -v true')
        pmc.mel.eval('FBXExport -f "%s" -s' % path.replace('\\', '/'))

    finally:
        pmc.undoInfo(closeChunk=True)
        pmc.undo()
    return path


def importRig(path=None):
    """
    Imports the given fbx file as a rig.
    For now this essentially just wraps importFbx().
    
    Args:
        path(str): An fbx file path. 

    Returns:
        list: A list of imported nodes.
    """
    nodes = importFbx(path)
    joints = pmc.ls(nodes, type='joint')

    root = getRootJoint()
    if root is not None:
        if not root.hasAttr('showRagdoll'):
            root.addAttr('showRagdoll', at='bool', dv=False)
            root.showRagdoll.set(cb=True)
        for joint in joints:
            if joint.name().endswith('_rb'):
                root.showRagdoll.connect(joint.visibility)
            joint.radius.set(5)

    return nodes


def exportRig(path=None):
    """
    Exports a rig from the current scene.
    This command relies on our static root joint existing in the scene.
    
    Args:
        path(str): A destination fbx file path.
    
    Returns:
        str: The exported file path.
    """
    # path = path or saveFbxDialog('Export Rig Dialog')
    path = path or os.path.join(getSceneCharacterAssetDirectory(), 'skeleton.fbx')

    # Find the root and bounding box
    root = getRootJoint()
    if root is None:
        raise RootJointException('Export rig failed, could not find a root joint in the scene.')
    box = getBoundingBox()

    try:
        pmc.undoInfo(openChunk=True)
        if root.getParent() is not None:
            pmc.parent(root, world=True)
        if box.getParent() is not None:
            pmc.parent(box, world=True)

        # Disconnect all connections and constraints
        for joint in [root] + getBindSkeleton():
            joint.message.disconnect(outputs=True)
            constraints = joint.getChildren(type='constraint')
            if len(constraints) > 0:
                pmc.delete(constraints)

        exportFbx([root, box], path, animation=False)
    finally:
        pmc.undoInfo(closeChunk=True)
        if not pmc.undoInfo(uqe=True, q=True):
            pmc.undo()

    # Convert to hkx
    ckcmd.importrig(path, os.path.dirname(path))


def textureSkin(meshes=None, albedo=None, normal=None, name='skywind'):
    """
    Assigns albedo and normal maps in order to be exported correctly as a skin.
    
    Args:
        meshes(list): A list of mesh nodes, defaults to the current selection. 
        albedo(str): An albedo file path. If none is given the user will be prompted to select one. 
        normal(str): A normal map file path. If none is given the user will be prompted to select one. 
        name(str): A name to append to material names. 
    """
    dir = os.path.dirname(pmc.sceneName())
    meshes = meshes or pmc.selected()
    meshes = getMeshes(meshes)
    albedo = albedo if albedo is not None else pmc.fileDialog2(fileFilter='*.dds', dir=dir,
                                                               caption='Albedo', fileMode=1) or []
    normal = normal if normal is not None else pmc.fileDialog2(fileFilter='*.dds', dir=os.path.dirname(albedo[0]),
                                                               caption='Normal', fileMode=1) or []

    # Create shader
    shader = pmc.shadingNode('blinn', name='%s_blinn' % name, asShader=True)
    shadingGroup = pmc.sets(name='%sSG' % shader, empty=True, renderable=True, noSurfaceShader=True)
    pmc.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shadingGroup)
    for channel in ['R', 'G', 'B']:
        pmc.setAttr('%s.ambientColor%s' % (shader, channel), 1)
    pmc.setAttr('%s.specularRollOff' % shader, 0.3)
    pmc.setAttr('%s.eccentricity' % shader, 0.2)

    # Add textures
    albedoNode = pmc.shadingNode("file", asTexture=True, n="%s_albedo" % name)
    pmc.setAttr('%s.fileTextureName' % albedoNode, albedo, type="string")
    pmc.connectAttr('%s.outColor' % albedoNode, '%s.color' % shader)

    normalNode = pmc.shadingNode("file", asTexture=True, n="%s_normal" % name)
    pmc.setAttr('%s.fileTextureName' % normalNode, normal, type="string")
    bumpNode = pmc.createNode('bump2d')
    pmc.connectAttr('%s.outAlpha' % normalNode, '%s.bumpValue' % bumpNode)
    pmc.setAttr('%s.bumpInterp' % bumpNode, 1)
    pmc.connectAttr('%s.outNormal' % bumpNode, '%s.normalCamera' % shader)

    for mesh in meshes:
        pmc.sets(shadingGroup, e=True, forceElement=mesh)


def exportSkin(meshes=None, path=None):
    """
    Exports the given mesh nodes as a skyrim skin fbx.
    If no meshes are given the current selected meshes will be used. If no meshes are selected all meshes skinned
    to the root skeleton will be used.
    
    Args:
        meshes(list): A list of meshes to export. 
        path(str): The destination fbx path. 

    Returns:
        str: The exported file path.
    """
    path = path or saveFbxDialog('Save Skin Dialog', dir=getSceneCharacterAssetDirectory())

    # Get the root skeleton
    root = getRootJoint()
    if root is None:
        raise RootJointException('Export rig failed, could not find a root joint in the scene.')
    rootSkeleton = [root] + root.listRelatives(ad=True, type='joint')

    def getSkinnedMeshes():
        clusters = set()
        for joint in rootSkeleton:
            for cluster in pmc.ls(pmc.listConnections(joint), type='skinCluster'):
                clusters.add(cluster)
        return [pmc.skinCluster(cluster, geometry=True, q=True)[0] for cluster in clusters]

    meshes = meshes or pmc.selected() or getSkinnedMeshes()
    meshes = getMeshes(meshes)

    if len(meshes) > 1:
        raise NotImplementedError('Multiple meshes selected for export. Currently we only support one mesh per skin.')

    # Check max influences
    for mesh in meshes:
        if not _checkMaxInfluences(mesh):
            raise MaxInfluenceException('Failed to export "%s". Skinning contains more than 4 influences.' % mesh)

    try:
        pmc.undoInfo(openChunk=True)

        # Set vertex colors to white
        for mesh in meshes:
            pmc.polyColorPerVertex(mesh, colorRGB=[1, 1, 1], a=1)

        # To fix certain issues with skinning we need to mess with the normals
        for mesh in meshes:
            pmc.bakePartialHistory(mesh, prePostDeformers=True)  # Delete Non-deformer history
            pmc.polyNormalPerVertex(mesh, unFreezeNormal=True)  # Unlock the normals
            pmc.polySoftEdge(mesh, a=180)  # Soften the normals
            pmc.bakePartialHistory(mesh, prePostDeformers=True)  # Delete Non-deformer history
            pmc.polyNormalPerVertex(mesh, freezeNormal=True)  # Lock the normals
            pmc.polySoftEdge(mesh, a=0)  # Harden the normals
            pmc.bakePartialHistory(mesh, prePostDeformers=True)  # Delete Non-deformer history

        # Remove all joint constraints
        constraints = root.listRelatives(ad=True, type='constraint')
        if len(constraints) > 0:
            pmc.delete(constraints)

        # Disconnect message connections
        for joint in rootSkeleton:
            joint.message.disconnect()
            if not joint.hasAttr(MATCH_ATTR_NAME):
                continue
            for input in joint.attr(MATCH_ATTR_NAME).inputs(plugs=True):
                input.disconnect(joint.attr(MATCH_ATTR_NAME))

        exportFbx(rootSkeleton + [mesh.getParent() for mesh in meshes], path=path)

    finally:
        pmc.undoInfo(closeChunk=True)
        pmc.undo()

    # Export nif
    ckcmd.importskin(path, os.path.dirname(path))


def isExportJoint(joint):
    """ Determines if the given joint is a child of a root joint. """
    parent = joint.getParent()
    while parent is not None and parent.getParent() is not None:
        parent = parent.getParent()
    if parent is None:
        return False
    return parent.nodeName() == ROOT_NAME


def validateJoints(joints=None):
    """
    Ensures the joints are valid for export.
    This mostly consists of ensuring it has a bone order attribute.
    
    Args:
        joints(list): A list of joints to validate. 
    """
    joints = joints if joints is not None else pmc.selected()
    joints = pmc.ls(joints, type='joint')

    for joint in joints:
        if not isExportJoint(joint):
            continue

        bone_attrs = {attr: attr.get() for attr in pmc.ls('*.bone_order')}

        # Add the bone order attribute
        if not joint.hasAttr('bone_order'):
            joint.addAttr('bone_order', at='long')
            joint.bone_order.set(cb=True)

        # Add a unique bone number
        for i in range(len(bone_attrs) + 1):
            if i not in bone_attrs.values():
                joint.bone_order.set(i)
                break


def addJoints(joints=None):
    """
    Adds the given joints to the export rig.
    If the joints are not a child of the root joint duplicates will be added.
    
    Args:
        joints(list): A list of joints, defaults to the current selection. 
        
    Returns:
        list: A list of added joints
    """
    joints = joints or pmc.selected()
    joints = pmc.ls(joints, type='joint')
    if len(joints) == 0:
        joints = [pmc.createNode('joint', name='newJoint', parent=getRootJoint())]

    newJoints = []
    for joint in joints:
        dupJoint = pmc.createNode('joint', name=joint.nodeName(),
                                  parent=getRootJoint() if not isExportJoint(joint) else joint)
        dupJoint.setMatrix(joint.getMatrix(worldSpace=True), worldSpace=True)
        if not isExportJoint(joint):
            matchJoints(joint, dupJoint)
        dupJoint.radius.set(joint.radius.get())
        newJoints.append(dupJoint)

    validateJoints(newJoints)
    return newJoints


def matchJoints(source, destination):
    """ Tags the source as a match of the destination. """
    if not source.hasAttr(MATCH_ATTR_NAME):
        source.addAttr(MATCH_ATTR_NAME, at='message')
    if not destination.hasAttr(MATCH_ATTR_NAME):
        destination.addAttr(MATCH_ATTR_NAME, at='message')
    if not pmc.isConnected(source.message, destination.attr(MATCH_ATTR_NAME)):
        source.message.connect(destination.attr(MATCH_ATTR_NAME), force=True)
    if not pmc.isConnected(destination.message, source.attr(MATCH_ATTR_NAME)):
        destination.message.connect(source.attr(MATCH_ATTR_NAME), force=True)


def retargetJoints(joints=None):
    """
    Retargets the given joints.
    This will match the source to the destination joints and mark them as matches.
    These matches can be used to retarget skins.
    
    Args:
        joints(list): A list of joints, defaults to the selected joints. 
    """
    joints = joints or pmc.selected(type='joint')
    matches = zip(joints[:len(joints)/2], joints[len(joints)/2:])

    for source, destination in matches:
        source.setTranslation(destination.getTranslation(space='world'), space='world')
        matchJoints(source, destination)


def bindRootSkeleton():
    """
    Binds the root skeleton to its matching joints.
    """
    for joint in getRootSkeleton():
        if not joint.hasAttr(MATCH_ATTR_NAME):
            continue
        inputs = joint.attr(MATCH_ATTR_NAME).inputs()
        if len(inputs) == 0:
            continue
        match = inputs[0].node()

        if pmc.parentConstraint(joint, q=True) is None:
            pmc.parentConstraint(match, joint, mo=True)


def retargetSkin(meshes=None):
    """
    Creates new meshes retargeted to the root skeleton.
    
    Args:
        meshes(list): A list of meshes, defaults to the current selection. 
    """
    meshes = meshes or pmc.selected()
    meshes = getMeshes(meshes)

    newMeshes = []
    for srcMesh in meshes:
        # Create a duplicate mesh
        dstParent = pmc.duplicate(srcMesh.getParent())
        pmc.parent(dstParent, world=True)

        # Copy the skinning
        srcCluster = pmc.ls(srcMesh.listHistory(), type='skinCluster')[0]
        dstCluster = pmc.skinCluster(dstParent, getBindSkeleton(), mi=4, tsb=True)
        pmc.copySkinWeights(ss=srcCluster, ds=dstCluster, noMirror=True)
        newMeshes.append(dstParent)

    # If more than one mesh selected, combine meshes
    if len(newMeshes) > 1:
        newMesh, newCluster = pmc.polyUniteSkinned(newMeshes, ch=False)
        pmc.delete(newMeshes)
        pmc.rename(newMesh, 'body')

    bindRootSkeleton()


def copyTagAttribiutes(srcRoot, dstRoot):
    """
    Copies animation tag attributes from the source root to the destination root.
    
    Args:
        source(Joint): A source root joint. 
        destination(Joint): A destination root joint.
    """
    for srcAttr in srcRoot.listAttr(userDefined=True):
        if not dstRoot.hasAttr(srcAttr.attrName()):
            cmd = srcAttr.__apimattr__().getAddAttrCmd(True)
            cmd = cmd.replace(';', ' %s;' % dstRoot)
            pmc.mel.eval(cmd)

        pmc.copyAttr(srcRoot, dstRoot, at=[srcAttr.attrName()], v=True)
        # Copy Animation
        if pmc.keyframe(srcRoot, at=[srcAttr.attrName()], q=True):
            pmc.copyKey(srcRoot, at=[srcAttr.attrName()])
            pmc.pasteKey(dstRoot, at=[srcAttr.attrName()])


def importAnimation(path=None):
    """
    Additively imports an animation onto an existing rig.
    
    Args:
        path(str): An fbx path to import. 
    """
    path = path or loadFbxDialog('Animation', dir=getSceneAnimationDirectory())
    importFbx(path, update=True)
    dstRoot = getRootJoint()

    tagPath = os.path.join(getSceneTagDirectory(), os.path.basename(path))
    nodes = importFbx(tagPath, update=False)

    # Find the source root in the imported nodes
    srcRoot = None
    for node in pmc.ls(nodes, type='joint'):
        if ROOT_NAME in node.nodeName():
            srcRoot = node
            break

    # Copy the attribute data form the source root to the destination
    copyTagAttribiutes(srcRoot, dstRoot)
    pmc.delete(nodes)


def setRetarget(node=None, target=None):
    """
    Sets the given nodes retarget to the given target node.
    
    Args:
        node(PyNode): A node to set the retarget of.
        target(PyNode): The target node, if None this will disconnect any existing connections..
    """
    selection = pmc.selected()
    node = node or selection[0]
    if target is None:
        if len(selection) > 1:
            target = selection[1]

    # Add and connect the retarget
    if not node.hasAttr(RETARGET_ATTR_NAME):
        node.addAttr(RETARGET_ATTR_NAME, at='message')
    if target:
        if not pmc.isConnected(target.message, node.attr(RETARGET_ATTR_NAME)):
            target.message.connect(node.attr(RETARGET_ATTR_NAME), force=True)
    else:
        node.attr(RETARGET_ATTR_NAME).disconnect()
    pmc.displayInfo('Defined retarget from %s to %s' % (target, node))


def getRetargets(joint):
    """
    Gets all retargets for a given joint.
    
    Args:
        joint(Joint): A skeleton joint.

    Returns:
        list: A list of nodes.
    """
    targets = set()
    for output in joint.message.outputs(plugs=True):
        if output.attrName() == RETARGET_ATTR_NAME:
            targets.add(output.node())
    return list(targets)


def testRetargets():
    """
    Test the retargets in the current scene.
    
    Returns:
        Joint: The newly created root skeleton.
    """
    # Add a namespace for duplicate nodes
    DUP_NAMESPACE = 'DUP'
    if not pmc.namespace(exists=DUP_NAMESPACE):
        pmc.namespace(add=DUP_NAMESPACE)

    # Duplicate the bind skeleton
    root = getRootJoint()
    dupRoot = pmc.duplicate(root)[0]
    dupSkeleton = [dupRoot] + dupRoot.listRelatives(ad=True, type='joint')

    # Add a namespace to duplicates
    for joint in dupSkeleton:
        pmc.rename(joint, '%s:%s' % (DUP_NAMESPACE, joint.nodeName()))
    pmc.rename(dupRoot, dupRoot.nodeName().replace('1', ''))

    # Bind duplicates to targets
    for joint in dupSkeleton:
        rigJoint = pmc.PyNode(joint.nodeName().split(':')[-1])
        for target in getRetargets(rigJoint):
            pmc.parentConstraint(joint, target, mo=True)


def bakeAnimation(nodes):
    """
    Bakes animation on the given nodes for the current timeline.
    
    Args:
        nodes(list): A list of nodes. 
    """
    try:
        pmc.refresh(su=True)
        start = pmc.playbackOptions(minTime=True, q=True)
        end = pmc.playbackOptions(maxTime=True, q=True)
        pmc.bakeResults(nodes, at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], t=(start, end), simulation=True)
    finally:
        pmc.refresh(su=False)


def retargetAnimation(animation=None, skeleton=None, force=False):
    """
    Creates a new maya scene that retargets the given animation onto the given skeleton scene.
    
    Returns:
        str: The newly created animation scene.
    """
    animation = animation or loadFbxDialog('Animation Source', dir=getSceneAnimationDirectory())

    # Find the skeleton scene
    if skeleton is None:
        characterAssetDir = getSceneCharacterAssetDirectory()
        if os.path.exists(os.path.join(characterAssetDir, 'skeleton.ma')):
            skeleton = os.path.join(characterAssetDir, 'skeleton.ma')
        else:
            skeleton = loadSceneDialog('Skeleton Scene', dir=characterAssetDir)

    # Create a new file and reference the skeleton
    try:
        pmc.newFile()
    except RuntimeError:
        if not force:
            result = saveScenePrompt()
            if result:
                pmc.saveFile()
        pmc.newFile(force=True)
    pmc.createReference(skeleton, ns=RIG_NAMESPACE)

    # Create a duplicate skeleton
    rigRoot = getRootJoint(RIG_NAMESPACE)
    pmc.duplicate(rigRoot)
    root = getRootJoint()

    # Bind controls to skeleton
    targets = []
    for joint in getBindSkeleton():
        rigJoint = pmc.PyNode('%s:%s' % (RIG_NAMESPACE, joint))
        for target in getRetargets(rigJoint):
            pmc.parentConstraint(joint, target, mo=True)
            targets.append(target)

    # Bind the root joint
    for target in getRetargets(rigRoot):
        pmc.parentConstraint(root, target, mo=True)
        targets.append(target)

    # Save the scene
    sceneName = animation.replace('.fbx', '.ma')
    pmc.saveAs(sceneName)

    # Import the animation
    importAnimation(animation)

    # Copy the tag attributes
    copyTagAttribiutes(root, rigRoot)

    # Bake the bind targets
    bakeAnimation(targets)

    # Delete the import skeleton
    pmc.delete(root)

    pmc.saveFile(force=True)

    # Flush undo (this process should not be undoable)
    pmc.flushUndo()


def batchRetargetAnimations(animations=None, skeleton=None):
    """
    Retargets all given animations.    
    
    Args:
        animations(list): A list of animation fbxs. 
        skeleton(str): A maya skeleton scene. 
    """
    animations = animations or loadFbxsDialog('Select Animations', dir=getSceneAnimationDirectory())

    # Prompt the user to save the current scene
    result = saveScenePrompt()
    if result:
        pmc.saveFile()

    for animation in animations:
        retargetAnimation(animation, skeleton, force=True)


def exportAnimation(path=None):
    """
    Bakes and exports animation on a rig in the scene.
    
    Args:
        path(str): An destination fbx path to export. 
    """
    if path is None:
        path = pmc.sceneName()
    path = path.replace('.ma', '.fbx')

    # Get the root joint
    root = None
    namespace = None
    for namespace in pmc.listNamespaces():
        root = getRootJoint(namespace)
        if root is not None:
            namespace = namespace
            break
    if root is None:
        raise RootJointException('Could not find a root in the scene with a namespace.')

    try:
        pmc.undoInfo(openChunk=True)

        # Create a duplicate root joint
        dupRoot = pmc.duplicate(root)[0]
        pmc.rename(dupRoot, root.nodeName().split(':')[-1])

        # Copy animation tags
        copyTagAttribiutes(root, dupRoot)

        # Bind skeleton
        constraints = []
        exportJoints = [dupRoot] + getBindSkeleton()
        for joint in [dupRoot] + getBindSkeleton():
            source = pmc.PyNode('%s:%s' % (namespace, joint.nodeName()))
            constraints.append(pmc.parentConstraint(source, joint))

        # Bake animation and remove constraints
        bakeAnimation(exportJoints)
        pmc.delete(constraints)

        # Export animation and convert to hkx
        exportFbx([dupRoot] + getBindSkeleton(), path=path, animation=True)
        ckcmd.importanimation(
            getSceneSkeletonHkx(legacy=True), path,
            getSceneAnimationDirectory(), cache_txt=getSceneCacheFile(),
            behavior_directory=getSceneBehaviorDirectory()
        )

        # TODO copy cache file to correct directory
    finally:
        pmc.undoInfo(closeChunk=True)
        # pmc.undo()


def batchExportAnimations(animations=None):
    """
    Batch exports each animation file to the destination folder.
    
    Args:
        animations(list): A list of maya filenames.
    """
    animations = animations or loadScenesDialog('Select Animations', dir=getSceneAnimationDirectory())

    # Prompt the user to save the current scene
    result = saveScenePrompt()
    if result:
        pmc.saveFile()

    for animation in animations:
        pmc.openFile(animation, force=True)
        exportAnimation(animation)


class FilePathException(BaseException):
    pass


class FbxException(BaseException):
    pass


class MaxInfluenceException(BaseException):
    pass


class DirectoryException(BaseException):
    pass


class RootJointException(BaseException):
    pass


class SaveSceneException(BaseException):
    pass