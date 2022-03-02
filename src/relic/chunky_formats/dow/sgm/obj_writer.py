from os.path import split, splitext, join, basename
from pathlib import Path
from typing import TextIO, BinaryIO, Optional

from ..common_chunks.imag import TxtrChunk
from ..common_chunks.imag_writer import ImagConverter
from .sgm import SgmChunky, SgmRsgmChunk
from ....file_formats.mesh_io import Float3
from ....file_formats.wavefront_obj import ObjWriter


def get_name_from_texture_path(path: str, strip_ext: bool = True) -> str:
    path = basename(path)
    if strip_ext:
        path, _ = splitext(path)
    return path


# writes the matlib name into an OBJ file
# the associated mtl should be generated appropriately
# for convenience, the path to the mtl is returned
def write_matlib_name(stream: TextIO, obj_path: str) -> str:
    dirname, filename = split(obj_path)
    filename, _ = splitext(filename)

    filename += ".mtl"

    matlib_writer = ObjWriter(stream)
    matlib_writer.write_material_library(filename)
    return join(dirname, filename)


def flip_float3(v: Float3, flip_x: bool = False, flip_y: bool = False, flip_z: bool = False) -> Float3:
    if not any([flip_x, flip_y, flip_z]):  # Used a list to avoid confusion with any((flip_x,flip_y,flip_z))
        return v
    x, y, z = v
    if flip_x:
        x *= -1
    if flip_y:
        y *= -1
    if flip_z:
        z *= -1
    return x, y, z


# def write_mslc_to_obj(stream: TextIO, chunk: MslcChunk, name: str = None, v_offset: int = 0, axis_fix: bool = True) -> int:
#     writer = ObjWriter(stream)
#     v_local_offset = 0
#
#     if name:
#         writer.write_object_name(name)
#
#     mesh = chunk.data
#     positions = mesh.positions()
#     normals = mesh.normals()
#     uvs = mesh.uvs()
#     if axis_fix:
#         positions = [flip_float3(p, flip_x=True) for p in positions]
#         normals = [flip_float3(n, flip_x=True) for n in normals]
#
#     writer.write_vertex_positions(positions)
#     writer.write_vertex_normals(normals)
#     writer.write_vertex_uvs(uvs)
#     v_local_offset += mesh.vertex_count()
#
#     for ibuffer in mesh.triangle_buffers:
#         name, triangle_buffer = ibuffer[0], ibuffer[1]
#         tex_name = get_name_from_texture_path(name)
#         writer.write_use_material(tex_name)
#         writer.write_index_faces(*triangle_buffer, offset=v_offset, zero_based=True, flip_winding=True)
#     return v_local_offset


# def write_msgr_mscl(stream: TextIO, chunk: MsgrChunk) -> int:
#     v_offset = 0
#     for i, mslc in enumerate(chunk.mslc):
#         # name = mslc # name from data?
#         name = chunk.data.items[i].name
#         v_offset += write_mslc_to_obj(stream, mslc, name, v_offset=v_offset)
#     return v_offset


def write_sgm_texture_stream(stream: BinaryIO, chunk: TxtrChunk, out_format: str = None, texconv_path: str = None):
    ImagConverter.Imag2Stream(chunk.imag, stream, out_format, texconv_path=texconv_path)


def write_sgm_texture(root: str, chunk: Optional[TxtrChunk], out_format: str = None, texconv_path: str = None):
    if not chunk:
        return
    p = Path(root)
    f = p / (str(basename(chunk.header.name)) + ("." + out_format if out_format else ""))
    with open(f, "wb") as handle:
        write_sgm_texture(handle, chunk, out_format, texconv_path)

#
# def fetch_textures_from_mslc(chunk: MslcChunk) -> Iterable[str]:
#     for tbuffer in chunk.data.triangle_buffers:
#         yield tbuffer[0]
#
#
# def fetch_textures_from_msgr(chunk: MsgrChunk) -> Iterable[str]:
#     for mslc in chunk.mslc:
#         for texture in fetch_textures_from_mslc(mslc):
#             yield texture
#

# def write_msgr_to_mtl(stream: TextIO, chunk: MsgrChunk, texture_root: str = None, texture_ext: str = None, force_valid: bool = True, basename_only: bool = False):
#     if texture_ext:
#         if texture_ext[0] != ".":
#             texture_ext = "." + texture_ext
#     else:
#         texture_ext = ""
#     textures = [t for t in fetch_textures_from_msgr(chunk)]
#     textures = set(textures)
#
#     mtl_writer = MtlWriter(stream)
#     for texture in textures:
#         tex_name = get_name_from_texture_path(texture)
#         mtl_writer.write_default_texture(tex_name)
#         full_texture = join(texture_root, texture) if texture_root else texture
#         full_texture += texture_ext
#         if force_valid:
#             d, b = split(full_texture)
#             full_texture = join(d, b.replace(" ", "_"))
#         if basename_only:
#             full_texture = basename(full_texture)
#         mtl_writer.write_texture_diffuse(full_texture)
#         mtl_writer.write_texture_alpha(full_texture)


def write_sgm(root: str, sgm: SgmChunky, out_format: str = None, texconv_path: str = None):
    raise NotImplementedError
    root, _ = splitext(root)
    p = Path(root)
    p.mkdir(exist_ok=True, parents=True)
    if isinstance(sgm.rsgm, SgmRsgmChunk):
        write_sgm_texture(root, sgm.rsgm.txtr, out_format, texconv_path)
        obj_path = p / (p.name + ".obj")
        with open(obj_path, "w") as obj_handle:
            mtl_path = write_matlib_name(obj_handle, str(obj_path))
            write_msgr_mscl(obj_handle, sgm.rsgm.mesh)
        with open(mtl_path, "w") as mtl_handle:
            write_msgr_to_mtl(mtl_handle, sgm.rsgm.msgr, str(p), out_format, basename_only=True)
    else:
        raise NotImplementedError
