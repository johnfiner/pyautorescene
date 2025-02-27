import os,re,subprocess
import re
from rescene import info, extract_files, reconstruct

class SRR:
    def __init__(self, filename, binary=None):
        if not os.path.isfile(filename):
            raise AttributeError("srr must be a file")

        if not filename.endswith(".srr"):
            raise AttributeError("srr file must have the .srr extension")

        self.filename = filename
        if binary is None:
            if os.name == 'posix':
                self.binary = '/usr/bin/srr'
            elif os.name == 'nt':
                self.binary = 'srr'
            else:
                self.binary = binary

    # check if compression method is used for RAR file
    def get_is_compressed(self):
        if info(self.filename)['compression']:
            return True

    # search an srr for all rar-files presents
    # returns array of FileInfo's
    def get_rars_name(self):
        matches = []

        for sfile in info(self.filename)['rar_files'].values():
            matches.append(sfile.file_name)

        return matches

    def get_rar_crc(self):
        matches = []

        for sfile in info(self.filename)['rar_files'].values():
            matches.append(sfile.crc32)

        return matches

    # search an srr for all non RAR files presents in all sfv file
    # returns array of FileInfo's
    def get_sfv_entries_name(self):
        matches = []

        for sfile in info(self.filename)['sfv_entries']:
            matches += (str(sfile).split())

        return matches[::2]

    # search an srr for all files presents in srr
    # returns array of FileInfo's
    def get_stored_files_name(self):
        matches = []

        for sfile in info(self.filename)['stored_files'].keys():
            if not sfile.endswith(".srs"):
                matches.append(sfile)

        return matches

    def get_archived_fname(self):
        matches = []

        for sfile, value in info(self.filename)['archived_files'].items():
            matches.append(sfile)

        return matches

    # search an srr for all archived-files that match given crc
    # returns array of FileInfo's matching the crc
    def get_archived_fname_by_crc(self, crc):
        matches = []

        for _, value in info(self.filename)['archived_files'].items():
            if crc == value.crc32.zfill(8):
                matches.append(value)

        return matches

    # search an srr for all archived-files that much a given filename
    # returns an array of FileInfo's matching the fname
    def get_archived_crc_by_fname(self, fname):
        matches = []

        for key, value in info(self.filename)['archived_files'].items():
            if fname == key:
                matches.append(value)

        return matches

    def get_srs(self, path):
        if not os.path.isdir(path):
            raise AttributeError("path must be a valid directory")

        matches = []
        for sfile in info(self.filename)['stored_files'].keys():
            if sfile.endswith(".srs"):
                result = extract_files(self.filename, path,
                                       extract_paths=True, packed_name=sfile)
                matches += result

        return matches

    def get_proof_filename(self):
        matches = []

        for sfile in info(self.filename)['stored_files'].keys():
            if sfile.endswith(".jpg") or sfile.endswith(".jpeg") or sfile.endswith(".png"):
                matches.append(sfile)

        return matches

    def extract_stored_files_regex(self, path, regex=".*"):
        if not os.path.isdir(path):
            raise AttributeError("path must be a valid directory")

        matches = []

        for key in info(self.filename)["stored_files"].keys():
            if re.search(regex, key):
                result = extract_files(self.filename, path,
                                       extract_paths=True, packed_name=key)
                matches += result

        return matches

    def reconstruct_rars(self, dinput, doutput, hints, rarfolder, tmpfolder):
        if not os.path.isdir(dinput):
            raise AttributeError("input folder must be a valid directory.")
        if not os.path.isdir(doutput):
            raise AttributeError("output folder must be a valid directory")
        if os.name == 'nt':
            if not os.path.isdir(rarfolder):
                raise AttributeError("rar folder must be a valid directory.")
            if not os.path.isdir(tmpfolder):
                os.mkdir(tmpfolder)

            try:
                res = reconstruct(self.filename, dinput, doutput, hints=hints,
                                  auto_locate_renamed=True, rar_executable_dir=rarfolder,
                                  tmp_dir=tmpfolder, extract_files=False)

                if res == -1:
                    raise ValueError("One or more of the original files already exist in " + doutput)
            except:
                raise
        else:
            try:
                res = reconstruct(self.filename, dinput, doutput, hints=hints,
                                  auto_locate_renamed=True, extract_files=False)

                if res == -1:
                    raise ValueError("One or more of the original files already exist in " + doutput)
            except:
                raise

        return True