import re
import struct
import hashlib

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from lifeograph_db_converter import Diary, Format


FILE_ID = 'LIFEOGRAPHDB'
SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32
HEADER_DELIM = b'\n\n'
HEADER_PART_DELIM = b'\n'
HEADER_KEY_VAL_DELIM = b' '
ENCYPTION_KEY = 'E'
YES_VALUE = 'y'
HASH_ALGORITHM = hashlib.sha256
CIPHER_ALGORITHM = algorithms.AES
CIPHER_MODE = modes.CFB


class LifeographDb110Format(Format):

    def __init__(self, password=None):
        super().__init__()
        self.password = password

    def decode(self, data):
        header, body = data.split(HEADER_DELIM, 1)
        file_id, *header_parts = header.split(HEADER_PART_DELIM)
        assert file_id.decode() == FILE_ID
        meta = {}
        for header_part in header_parts:
            attr_name, attr_value = header_part.split(HEADER_KEY_VAL_DELIM, 1)
            meta[attr_name.decode()] = attr_value.decode()
        if meta[ENCYPTION_KEY].startswith(YES_VALUE):
            body = self.decrypt(body, self.password.encode())
        return self.parse_content(body)

    def encode(self, diary):
        # TODO: implement
        raise NotImplementedError

    def parse(self, data):
        if isinstance(data, str):
            data = data.encode()
        return data

    def dump(self, data):
        if isinstance(data, bytes):
            data = data.decode()
        return data

    def decrypt(self, body, password):
        content_size = len(body) - (SALT_SIZE + IV_SIZE)
        salt, iv, encrypted_content = struct.unpack('{}s{}s{}s'.format(SALT_SIZE, IV_SIZE, content_size), body)
        key = self.expand_key(password, salt)
        cipher = Cipher(CIPHER_ALGORITHM(key), CIPHER_MODE(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        content = decryptor.update(encrypted_content) + decryptor.finalize()
        assert content[0] == password[0] or content[1] == b'\n'
        return content[2:]

    def expand_key(self, password, salt):
        m = HASH_ALGORITHM()
        m.update(salt)
        m.update(password)
        return m.digest()

    def parse_content(self, content):
        diary = Diary()
        meta_data, entries_data = content.split(b'\n\n', 1)
        # Tag and chapters
        meta_lines = meta_data.split(b'\n')
        meta_mapping = {r'^.{,2}$': self.parse_dummy,
                        r'^ID(\d+)$': self.parse_meta_id,
                        r'^T(.)(.+)$': self.parse_meta_tag_categories,
                        r'^t.(.+)$': self.parse_meta_tags,
                        r'^C(.)(.+)$': self.parse_meta_chapter_categories,
                        r'^o(.)((\d+)\t)?(.+)$': self.parse_meta_o_chapters,
                        r'^c(.)((\d+)\t)?(.+)$': self.parse_meta_chapters,
                        r'^d.(\d+)$': self.parse_meta_chapter_timestamp,
                        r'^M(.)(.+)$': self.parse_meta_theme,
                        r'^m(.)(.+)$': self.parse_meta_theme_config,
                        r'^O(.)(.+)$': self.parse_meta_options,
                        r'^l.(.+)$': self.parse_meta_language,
                        r'^S.(\d+)$': self.parse_meta_startup_action,
                        r'^L.(\d+)$': self.parse_meta_last_element,
                        r'^([um]).*$': self.parse_entries_tag_theme,
                        r'^f.*$': self.parse_entries_filter,
                        }
        self.map_block(meta_lines, meta_mapping, diary)
        # Entries
        entries_lines = entries_data.split(b'\n')
        entries_mapping = {r'^.{,1}$': self.parse_dummy,
                           r'^ID(\d+)$': self.parse_meta_id,
                           r'^([Ee])(.)(([^\d])([^\d]))?(\d+)$': self.parse_entries_entry,
                           r'^D([rhs])(\d+)$': self.parse_entries_date,
                           r'^M.(.+)$': self.parse_entries_theme,
                           r'^T.(.+)$': self.parse_entries_tag,
                           r'^l.(.+)$': self.parse_entries_language,
                           r'^P.(.*)$': self.parse_entries_paragraph,
                           }
        self.map_block(entries_lines, entries_mapping, diary)
        return diary

    def map_block(self, lines, mapping, diary):
        for line in lines:
            line = line.decode()
            match = None
            for regexp, func in mapping.items():
                match = re.match(regexp, line)
                if match:
                    func(match, diary)
                    break
            if not match:
                raise ValueError('Unrecognized line: "{}"'.format(line))

    def parse_dummy(self, m, diary):
        pass

    def parse_meta_id(self, m, diary):
        diary.last_id = int(m.group(1))

    def parse_meta_tag_categories(self, m, diary):
        diary.tag_categories.append(dict(
            expanded=m.group(1) == 'e',
            name=m.group(2),
        ))

    def parse_meta_tags(self, m, diary):
        diary.tags.append(dict(
            name=m.group(1),
        ))

    def parse_meta_chapter_categories(self, m, diary):
        # TODO:
        # if (line[1] == 'c' || m_ptr2chapter_ctg_cur == NULL) // for v73
        #     m_ptr2chapter_ctg_cur = ptr2chapter_ctg;
        diary.chapter_categories.append(dict(
            name=m.group(2),
        ))

    def parse_meta_o_chapters(self, m, diary):
        # TODO: m_topics
        diary.chapters.append(dict(
            expanded=m.group(1) == 'e',
            timestamp=int(m.group(3) or '0'),
            name=m.group(4),
        ))

    def parse_meta_chapters(self, m, diary):
        assert len(diary.chapter_categories) > 0
        diary.chapters.append(dict(
            expanded=m.group(1) == 'e',
            timestamp=int(m.group(3) or '0'),
            name=m.group(4),
            chapter=diary.chapter_categories[-1]
        ))

    def parse_meta_chapter_timestamp(self, m, diary):
        diary.chapters[-1]['timestamp'] = int(m.group(1))

    def parse_meta_theme(self, m, diary):
        theme = dict(name=m.group(2))
        diary.themes.append(theme)
        if m.group(1) == 'd':
            diary.default_theme = theme

    def parse_meta_theme_config(self, m, diary):
        assert len(diary.themes) > 0
        mapping = {'f': 'font',
                   'b': 'color_base',
                   't': 'color_text',
                   'h': 'color_heading',
                   's': 'color_subheading',
                   'l': 'color_highlight'}
        diary.themes[-1][mapping[m.group(1)]] = m.group(2)

    def parse_meta_options(self, m, diary):
        if len(m.group(2)) < 2:
            return
        if m.group(1) == 's':
            diary.language = 'en'
            # TODO:
            # m_option_sorting_criteria = line[3];

    def parse_meta_language(self, m, diary):
        diary.language = m.group(1)

    def parse_meta_startup_action(self, m, diary):
        diary.startup_action = int(m.group(1))

    def parse_meta_last_element(self, m, diary):
        diary.last_element = int(m.group(1))

    def parse_entries_entry(self, m, diary):
        # TODO: m.group(4) == 'h' # filter defauult
        # TODO: m.group(5) # todo status
        diary.entries.append(dict(
            trashed=m.group(1) == 'e',
            favorite=m.group(2) == 'f',
            timestamp=int(m.group(6)),
            themes=[],
            tags=[],
            paragraphs=[],
            language=None,
        ))

    def parse_entries_date(self, m, diary):
        key = {'r': 'date_created',
               'h': 'date_changed',
               's': 'date_status',
               }[m.group(1)]
        diary.entries[-1].update({key: int(m.group(2))})

    def parse_entries_theme(self, m, diary):
        theme_name = m.group(1)
        diary.entries[-1]['themes'].append(next(theme for theme in diary.themes if theme['name'] == theme_name))

    def parse_entries_tag(self, m, diary):
        tag_name = m.group(1)
        diary.entries[-1]['tags'].append(next(tag for tag in diary.tags if tag['name'] == tag_name))

    def parse_entries_language(self, m, diary):
        diary.entries[-1]['language'] = m.group(1)

    def parse_entries_paragraph(self, m, diary):
        diary.entries[-1]['paragraphs'].append(m.group(1))

    def parse_entries_tag_theme(self, m, diary):
        pass # TODO: do something

    def parse_entries_filter(self, m, diary):
        pass  # TODO: do something
