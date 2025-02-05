// Mapping von Zenon-IDs zu OJS Journal Codes
export const ojsZenonMapping = {
    '000054957': 'aa',
    '000055021': 'brgk',
    '000098143': 'chiron',
    '001376930': 'efb', // TODO: kein übergeordneter Datensatz in Zenon
    '001376922': 'ejb', // TODO: kein übergeordneter Datensatz in Zenon
    '000054792': 'ger',
    '000055658': 'mm',
    '000057152': 'BaM',
    '000146522': 'mdaik',
    '000036080': 'mdaik',
    '000036059': 'AMIran',
    '000814258': 'test'
} as { [index: string]: string };

export const allowedFileExtensions = ['pdf', 'tif', 'tiff', 'zip', 'txt'];

export const ignoredDirectoryContents = ['__MACOSX', '@eaDir', 'Thumbs.db', '.DS_Store', '.Info', '.cilantro_info'];

export const backendUri = process.env.VUE_APP_BACKEND_URI || '/api';
