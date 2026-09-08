'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Lock, 
  Unlock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Eye,
  EyeOff,
  Key,
  Fingerprint,
  IdCard,
  CreditCard,
  Smartphone,
  Tablet,
  Laptop,
  Desktop,
  Server,
  Router,
  Switch,
  Hub,
  Antenna,
  Satellite,
  Radio,
  Tv,
  Gamepad2,
  Headphones,
  Speaker,
  Webcam,
  Microphone,
  Keyboard,
  Mouse,
  Touchpad,
  Stylus,
  Pen,
  Eraser,
  Paintbrush,
  Palette,
  Scissors,
  Paperclip,
  Stapler,
  Calculator,
  Ruler,
  Compass,
  Protractor,
  Triangle,
  Square,
  Circle,
  Hexagon,
  Pentagon,
  Octagon,
  Star,
  Heart,
  Diamond,
  Club,
  Spade,
  Music,
  MusicalNote,
  Music2,
  Music3,
  Music4,
  Play,
  Pause,
  Square as SquareIcon,
  Circle as CircleIcon,
  Triangle as TriangleIcon,
  Pentagon as PentagonIcon,
  Hexagon as HexagonIcon,
  Octagon as OctagonIcon,
  Star as StarIcon2,
  Heart as HeartIcon,
  Diamond as DiamondIcon,
  Club as ClubIcon,
  Spade as SpadeIcon,
  Zap,
  Activity,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
  AreaChart,
  RadarChart,
  ScatterChart,
  Heatmap,
  TreeMap,
  Sunburst,
  Funnel,
  Gauge,
  Target,
  Award,
  Trophy,
  Medal,
  Crown,
  Gem,
  Coins,
  Banknote,
  Wallet,
  CreditCard as CreditCardIcon,
  Gift,
  Package,
  Box,
  Archive,
  Folder,
  FolderOpen,
  File,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  FileCode,
  FilePlus,
  FileMinus,
  FileSearch,
  FileCheck,
  FileX,
  FileWarning,
  FileQuestion,
  FileLock,
  FileUnlock,
  FileSignature,
  FileDigit,
  FileSpreadsheet,
  FileDatabase,
  FileArchive,
  FileOutput,
  FileInput,
  FileSymlink,
  FileJson,
  FileXml,
  FileYml,
  FileToml,
  FileIni,
  FileConf,
  FileConfig,
  FileSettings,
  FileTerminal,
  FileCode2,
  FileDiff,
  FileMerge,
  FilePatch,
  FileGit,
  FileGithub,
  FileGitlab,
  FileBitbucket,
  FileAzure,
  FileAws,
  FileGoogle,
  FileMicrosoft,
  FileApple,
  FileLinux,
  FileWindows,
  FileMac,
  FileAndroid,
  FileIos,
  FileWeb,
  FileCloud,
  FileDownload,
  FileUpload,
  FileSync,
  FileBackup,
  FileRestore,
  FileExport,
  FileImport,
  FileCopy,
  FileMove,
  FileRename,
  FileDelete,
  FileTrash,
  FileRecycle,
  FileUnarchive,
  FileCompress,
  FileDecompress,
  FileEncrypt,
  FileDecrypt,
  FileSign,
  FileVerify,
  FileHash,
  FileChecksum,
  FileMd5,
  FileSha1,
  FileSha256,
  FileSha512,
  FileRsa,
  FileEcdsa,
  FileDsa,
  FilePgp,
  FileGpg,
  FileSsl,
  FileTls,
  FileHttps,
  FileHttp,
  FileFtp,
  FileSftp,
  FileSsh,
  FileTelnet,
  FileRdp,
  FileVnc,
  FileRfb,
  FileRtmp,
  FileRtsp,
  FileMms,
  FileRtsp2,
  FileHls,
  FileDash,
  FileMpeg,
  FileMp4,
  FileAvi,
  FileMov,
  FileWmv,
  FileFlv,
  FileWebm,
  FileMkv,
  File3gp,
  FileM4v,
  FileOgv,
  FileOgg,
  FileWav,
  FileMp3,
  FileFlac,
  FileAac,
  FileOgg2,
  FileWma,
  FileM4a,
  FileOpus,
  FileSpeex,
  FileVorbis,
  FileAiff,
  FileAu,
  FileRa,
  FileWavPack,
  FileTta,
  FileMpc,
  FileWv,
  FileOptimFrog,
  FileLa,
  FileWavPack2,
  FileTak,
  FileOfr,
  FileOfs,
  FileOfr2,
  FileOfs2,
  FileOfr3,
  FileOfs3,
  FileOfr4,
  FileOfs4,
  FileOfr5,
  FileOfs5,
  FileOfr6,
  FileOfs6,
  FileOfr7,
  FileOfs7,
  FileOfr8,
  FileOfs8,
  FileOfr9,
  FileOfs9,
  FileOfr10,
  FileOfs10,
  FileOfr11,
  FileOfs11,
  FileOfr12,
  FileOfs12,
  FileOfr13,
  FileOfs13,
  FileOfr14,
  FileOfs14,
  FileOfr15,
  FileOfs15,
  FileOfr16,
  FileOfs16,
  FileOfr17,
  FileOfs17,
  FileOfr18,
  FileOfs18,
  FileOfr19,
  FileOfs19,
  FileOfr20,
  FileOfs20,
  FileOfr21,
  FileOfs21,
  FileOfr22,
  FileOfs22,
  FileOfr23,
  FileOfs23,
  FileOfr24,
  FileOfs24,
  FileOfr25,
  FileOfs25,
  FileOfr26,
  FileOfs26,
  FileOfr27,
  FileOfs27,
  FileOfr28,
  FileOfs28,
  FileOfr29,
  FileOfs29,
  FileOfr30,
  FileOfs30,
  FileOfr31,
  FileOfs31,
  FileOfr32,
  FileOfs32,
  FileOfr33,
  FileOfs33,
  FileOfr34,
  FileOfs34,
  FileOfr35,
  FileOfs35,
  FileOfr36,
  FileOfs36,
  FileOfr37,
  FileOfs37,
  FileOfr38,
  FileOfs38,
  FileOfr39,
  FileOfs39,
  FileOfr40,
  FileOfs40,
  FileOfr41,
  FileOfs41,
  FileOfr42,
  FileOfs42,
  FileOfr43,
  FileOfs43,
  FileOfr44,
  FileOfs44,
  FileOfr45,
  FileOfs45,
  FileOfr46,
  FileOfs46,
  FileOfr47,
  FileOfs47,
  FileOfr48,
  FileOfs48,
  FileOfr49,
  FileOfs49,
  FileOfr50,
  FileOfs50,
  FileOfr51,
  FileOfs51,
  FileOfr52,
  FileOfs52,
  FileOfr53,
  FileOfs53,
  FileOfr54,
  FileOfs54,
  FileOfr55,
  FileOfs55,
  FileOfr56,
  FileOfs56,
  FileOfr57,
  FileOfs57,
  FileOfr58,
  FileOfs58,
  FileOfr59,
  FileOfs59,
  FileOfr60,
  FileOfs60,
  FileOfr61,
  FileOfs61,
  FileOfr62,
  FileOfs62,
  FileOfr63,
  FileOfs63,
  FileOfr64,
  FileOfs64,
  FileOfr65,
  FileOfs65,
  FileOfr66,
  FileOfs66,
  FileOfr67,
  FileOfs67,
  FileOfr68,
  FileOfs68,
  FileOfr69,
  FileOfs69,
  FileOfr70,
  FileOfs70,
  FileOfr71,
  FileOfs71,
  FileOfr72,
  FileOfs72,
  FileOfr73,
  FileOfs73,
  FileOfr74,
  FileOfs74,
  FileOfr75,
  FileOfs75,
  FileOfr76,
  FileOfs76,
  FileOfr77,
  FileOfs77,
  FileOfr78,
  FileOfs78,
  FileOfr79,
  FileOfs79,
  FileOfr80,
  FileOfs80,
  FileOfr81,
  FileOfs81,
  FileOfr82,
  FileOfs82,
  FileOfr83,
  FileOfs83,
  FileOfr84,
  FileOfs84,
  FileOfr85,
  FileOfs85,
  FileOfr86,
  FileOfs86,
  FileOfr87,
  FileOfs87,
  FileOfr88,
  FileOfs88,
  FileOfr89,
  FileOfs89,
  FileOfr90,
  FileOfs90,
  FileOfr91,
  FileOfs91,
  FileOfr92,
  FileOfs92,
  FileOfr93,
  FileOfs93,
  FileOfr94,
  FileOfs94,
  FileOfr95,
  FileOfs95,
  FileOfr96,
  FileOfs96,
  FileOfr97,
  FileOfs97,
  FileOfr98,
  FileOfs98,
  FileOfr99,
  FileOfs99,
  FileOfr100,
  FileOfs100,
  FileOfr101,
  FileOfs101,
  FileOfr102,
  FileOfs102,
  FileOfr103,
  FileOfs103,
  FileOfr104,
  FileOfs104,
  FileOfr105,
  FileOfs105,
  FileOfr106,
  FileOfs106,
  FileOfr107,
  FileOfs107,
  FileOfr108,
  FileOfs108,
  FileOfr109,
  FileOfs109,
  FileOfr110,
  FileOfs110,
  FileOfr111,
  FileOfs111,
  FileOfr112,
  FileOfs112,
  FileOfr113,
  FileOfs113,
  FileOfr114,
  FileOfs114,
  FileOfr115,
  FileOfs115,
  FileOfr116,
  FileOfs116,
  FileOfr117,
  FileOfs117,
  FileOfr118,
  FileOfs118,
  FileOfr119,
  FileOfs119,
  FileOfr120,
  FileOfs120,
  FileOfr121,
  FileOfs121,
  FileOfr122,
  FileOfs122,
  FileOfr123,
  FileOfs123,
  FileOfr124,
  FileOfs124,
  FileOfr125,
  FileOfs125,
  FileOfr126,
  FileOfs126,
  FileOfr127,
  FileOfs127,
  FileOfr128,
  FileOfs128,
  FileOfr129,
  FileOfs129,
  FileOfr130,
  FileOfs130,
  FileOfr131,
  FileOfs131,
  FileOfr132,
  FileOfs132,
  FileOfr133,
  FileOfs133,
  FileOfr134,
  FileOfs134,
  FileOfr135,
  FileOfs135,
  FileOfr136,
  FileOfs136,
  FileOfr137,
  FileOfs137,
  FileOfr138,
  FileOfs138,
  FileOfr139,
  FileOfs139,
  FileOfr140,
  FileOfs140,
  FileOfr141,
  FileOfs141,
  FileOfr142,
  FileOfs142,
  FileOfr143,
  FileOfs143,
  FileOfr144,
  FileOfs144,
  FileOfr145,
  FileOfs145,
  FileOfr146,
  FileOfs146,
  FileOfr147,
  FileOfs147,
  FileOfr148,
  FileOfs148,
  FileOfr149,
  FileOfs149,
  FileOfr150,
  FileOfs150,
  FileOfr151,
  FileOfs151,
  FileOfr152,
  FileOfs152,
  FileOfr153,
  FileOfs153,
  FileOfr154,
  FileOfs154,
  FileOfr155,
  FileOfs155,
  FileOfr156,
  FileOfs156,
  FileOfr157,
  FileOfs157,
  FileOfr158,
  FileOfs158,
  FileOfr159,
  FileOfs159,
  FileOfr160,
  FileOfs160,
  FileOfr161,
  FileOfs161,
  FileOfr162,
  FileOfs162,
  FileOfr163,
  FileOfs163,
  FileOfr164,
  FileOfs164,
  FileOfr165,
  FileOfs165,
  FileOfr166,
  FileOfs166,
  FileOfr167,
  FileOfs167,
  FileOfr168,
  FileOfs168,
  FileOfr169,
  FileOfs169,
  FileOfr170,
  FileOfs170,
  FileOfr171,
  FileOfs171,
  FileOfr172,
  FileOfs172,
  FileOfr173,
  FileOfs173,
  FileOfr174,
  FileOfs174,
  FileOfr175,
  FileOfs175,
  FileOfr176,
  FileOfs176,
  FileOfr177,
  FileOfs177,
  FileOfr178,
  FileOfs178,
  FileOfr179,
  FileOfs179,
  FileOfr180,
  FileOfs180,
  FileOfr181,
  FileOfs181,
  FileOfr182,
  FileOfs182,
  FileOfr183,
  FileOfs183,
  FileOfr184,
  FileOfs184,
  FileOfr185,
  FileOfs185,
  FileOfr186,
  FileOfs186,
  FileOfr187,
  FileOfs187,
  FileOfr188,
  FileOfs188,
  FileOfr189,
  FileOfs189,
  FileOfr190,
  FileOfs190,
  FileOfr191,
  FileOfs191,
  FileOfr192,
  FileOfs192,
  FileOfr193,
  FileOfs193,
  FileOfr194,
  FileOfs194,
  FileOfr195,
  FileOfs195,
  FileOfr196,
  FileOfs196,
  FileOfr197,
  FileOfs197,
  FileOfr198,
  FileOfs198,
  FileOfr199,
  FileOfs199,
  FileOfr200,
  FileOfs200,
  FileOfr201,
  FileOfs201,
  FileOfr202,
  FileOfs202,
  FileOfr203,
  FileOfs203,
  FileOfr204,
  FileOfs204,
  FileOfr205,
  FileOfs205,
  FileOfr206,
  FileOfs206,
  FileOfr207,
  FileOfs207,
  FileOfr208,
  FileOfs208,
  FileOfr209,
  FileOfs209,
  FileOfr210,
  FileOfs210,
  FileOfr211,
  FileOfs211,
  FileOfr212,
  FileOfs212,
  FileOfr213,
  FileOfs213,
  FileOfr214,
  FileOfs214,
  FileOfr215,
  FileOfs215,
  FileOfr216,
  FileOfs216,
  FileOfr217,
  FileOfs217,
  FileOfr218,
  FileOfs218,
  FileOfr219,
  FileOfs219,
  FileOfr220,
  FileOfs220,
  FileOfr221,
  FileOfs221,
  FileOfr222,
  FileOfs222,
  FileOfr223,
  FileOfs223,
  FileOfr224,
  FileOfs224,
  FileOfr225,
  FileOfs225,
  FileOfr226,
  FileOfs226,
  FileOfr227,
  FileOfs227,
  FileOfr228,
  FileOfs228,
  FileOfr229,
  FileOfs229,
  FileOfr230,
  FileOfs230,
  FileOfr231,
  FileOfs231,
  FileOfr232,
  FileOfs232,
  FileOfr233,
  FileOfs233,
  FileOfr234,
  FileOfs234,
  FileOfr235,
  FileOfs235,
  FileOfr236,
  FileOfs236,
  FileOfr237,
  FileOfs237,
  FileOfr238,
  FileOfs238,
  FileOfr239,
  FileOfs239,
  FileOfr240,
  FileOfs240,
  FileOfr241,
  FileOfs241,
  FileOfr242,
  FileOfs242,
  FileOfr243,
  FileOfs243,
  FileOfr244,
  FileOfs244,
  FileOfr245,
  FileOfs245,
  FileOfr246,
  FileOfs246,
  FileOfr247,
  FileOfs247,
  FileOfr248,
  FileOfs248,
  FileOfr249,
  FileOfs249,
  FileOfr250,
  FileOfs250,
  FileOfr251,
  FileOfs251,
  FileOfr252,
  FileOfs252,
  FileOfr253,
  FileOfs253,
  FileOfr254,
  FileOfs254,
  FileOfr255,
  FileOfs255,
  FileOfr256,
  FileOfs256,
  FileOfr257,
  FileOfs257,
  FileOfr258,
  FileOfs258,
  FileOfr259,
  FileOfs259,
  FileOfr260,
  FileOfs260,
  FileOfr261,
  FileOfs261,
  FileOfr262,
  FileOfs262,
  FileOfr263,
  FileOfs263,
  FileOfr264,
  FileOfs264,
  FileOfr265,
  FileOfs265,
  FileOfr266,
  FileOfs266,
  FileOfr267,
  FileOfs267,
  FileOfr268,
  FileOfs268,
  FileOfr269,
  FileOfs269,
  FileOfr270,
  FileOfs270,
  FileOfr271,
  FileOfs271,
  FileOfr272,
  FileOfs272,
  FileOfr273,
  FileOfs273,
  FileOfr274,
  FileOfs274,
  FileOfr275,
  FileOfs275,
  FileOfr276,
  FileOfs276,
  FileOfr277,
  FileOfs277,
  FileOfr278,
  FileOfs278,
  FileOfr279,
  FileOfs279,
  FileOfr280,
  FileOfs280,
  FileOfr281,
  FileOfs281,
  FileOfr282,
  FileOfs282,
  FileOfr283,
  FileOfs283,
  FileOfr284,
  FileOfs284,
  FileOfr285,
  FileOfs285,
  FileOfr286,
  FileOfs286,
  FileOfr287,
  FileOfs287,
  FileOfr288,
  FileOfs288,
  FileOfr289,
  FileOfs289,
  FileOfr290,
  FileOfs290,
  FileOfr291,
  FileOfs291,
  FileOfr292,
  FileOfs292,
  FileOfr293,
  FileOfs293,
  FileOfr294,
  FileOfs294,
  FileOfr295,
  FileOfs295,
  FileOfr296,
  FileOfs296,
  FileOfr297,
  FileOfs297,
  FileOfr298,
  FileOfs298,
  FileOfr299,
  FileOfs299,
  FileOfr300,
  FileOfs300,
  FileOfr301,
  FileOfs301,
  FileOfr302,
  FileOfs302,
  FileOfr303,
  FileOfs303,
  FileOfr304,
  FileOfs304,
  FileOfr305,
  FileOfs305,
  FileOfr306,
  FileOfs306,
  FileOfr307,
  FileOfs307,
  FileOfr308,
  FileOfs308,
  FileOfr309,
  FileOfs309,
  FileOfr310,
  FileOfs310,
  FileOfr311,
  FileOfs311,
  FileOfr312,
  FileOfs312,
  FileOfr313,
  FileOfs313,
  FileOfr314,
  FileOfs314,
  FileOfr315,
  FileOfs315,
  FileOfr316,
  FileOfs316,
  FileOfr317,
  FileOfs317,
  FileOfr318,
  FileOfs318,
  FileOfr319,
  FileOfs319,
  FileOfr320,
  FileOfs320,
  FileOfr321,
  FileOfs321,
  FileOfr322,
  FileOfs322,
  FileOfr323,
  FileOfs323,
  FileOfr324,
  FileOfs324,
  FileOfr325,
  FileOfs325,
  FileOfr326,
  FileOfs326,
  FileOfr327,
  FileOfs327,
  FileOfr328,
  FileOfs328,
  FileOfr329,
  FileOfs329,
  FileOfr330,
  FileOfs330,
  FileOfr331,
  FileOfs331,
  FileOfr332,
  FileOfs332,
  FileOfr333,
  FileOfs333,
  FileOfr334,
  FileOfs334,
  FileOfr335,
  FileOfs335,
  FileOfr336,
  FileOfs336,
  FileOfr337,
  FileOfs337,
  FileOfr338,
  FileOfs338,
  FileOfr339,
  FileOfs339,
  FileOfr340,
  FileOfs340,
  FileOfr341,
  FileOfs341,
  FileOfr342,
  FileOfs342,
  FileOfr343,
  FileOfs343,
  FileOfr344,
  FileOfs344,
  FileOfr345,
  FileOfs345,
  FileOfr346,
  FileOfs346,
  FileOfr347,
  FileOfs347,
  FileOfr348,
  FileOfs348,
  FileOfr349,
  FileOfs349,
  FileOfr350,
  FileOfs350,
  FileOfr351,
  FileOfs351,
  FileOfr352,
  FileOfs352,
  FileOfr353,
  FileOfs353,
  FileOfr354,
  FileOfs354,
  FileOfr355,
  FileOfs355,
  FileOfr356,
  FileOfs356,
  FileOfr357,
  FileOfs357,
  FileOfr358,
  FileOfs358,
  FileOfr359,
  FileOfs359,
  FileOfr360,
  FileOfs360,
  FileOfr361,
  FileOfs361,
  FileOfr362,
  FileOfs362,
  FileOfr363,
  FileOfs363,
  FileOfr364,
  FileOfs364,
  FileOfr365,
  FileOfs365,
  FileOfr366,
  FileOfs366,
  FileOfr367,
  FileOfs367,
  FileOfr368,
  FileOfs368,
  FileOfr369,
  FileOfs369,
  FileOfr370,
  FileOfs370,
  FileOfr371,
  FileOfs371,
  FileOfr372,
  FileOfs372,
  FileOfr373,
  FileOfs373,
  FileOfr374,
  FileOfs374,
  FileOfr375,
  FileOfs375,
  FileOfr376,
  FileOfs376,
  FileOfr377,
  FileOfs377,
  FileOfr378,
  FileOfs378,
  FileOfr379,
  FileOfs379,
  FileOfr380,
  FileOfs380,
  FileOfr381,
  FileOfs381,
  FileOfr382,
  FileOfs382,
  FileOfr383,
  FileOfs383,
  FileOfr384,
  FileOfs384,
  FileOfr385,
  FileOfs385,
  FileOfr386,
  FileOfs386,
  FileOfr387,
  FileOfs387,
  FileOfr388,
  FileOfs388,
  FileOfr389,
  FileOfs389,
  FileOfr390,
  FileOfs390,
  FileOfr391,
  FileOfs391,
  FileOfr392,
  FileOfs392,
  FileOfr393,
  FileOfs393,
  FileOfr394,
  FileOfs394,
  FileOfr395,
  FileOfs395,
  FileOfr396,
  FileOfs396,
  FileOfr397,
  FileOfs397,
  FileOfr398,
  FileOfs398,
  FileOfr399,
  FileOfs399,
  FileOfr400,
  FileOfs400,
  FileOfr401,
  FileOfs401,
  FileOfr402,
  FileOfs402,
  FileOfr403,
  FileOfs403,
  FileOfr404,
  FileOfs404,
  FileOfr405,
  FileOfs405,
  FileOfr406,
  FileOfs406,
  FileOfr407,
  FileOfs407,
  FileOfr408,
  FileOfs408,
  FileOfr409,
  FileOfs409,
  FileOfr410,
  FileOfs410,
  FileOfr411,
  FileOfs411,
  FileOfr412,
  FileOfs412,
  FileOfr413,
  FileOfs413,
  FileOfr414,
  FileOfs414,
  FileOfr415,
  FileOfs415,
  FileOfr416,
  FileOfs416,
  FileOfr417,
  FileOfs417,
  FileOfr418,
  FileOfs418,
  FileOfr419,
  FileOfs419,
  FileOfr420,
  FileOfs420,
  FileOfr421,
  FileOfs421,
  FileOfr422,
  FileOfs422,
  FileOfr423,
  FileOfs423,
  FileOfr424,
  FileOfs424,
  FileOfr425,
  FileOfs425,
  FileOfr426,
  FileOfs426,
  FileOfr427,
  FileOfs427,
  FileOfr428,
  FileOfs428,
  FileOfr429,
  FileOfs429,
  FileOfr430,
  FileOfs430,
  FileOfr431,
  FileOfs431,
  FileOfr432,
  FileOfs432,
  FileOfr433,
  FileOfs433,
  FileOfr434,
  FileOfs434,
  FileOfr435,
  FileOfs435,
  FileOfr436,
  FileOfs436,
  FileOfr437,
  FileOfs437,
  FileOfr438,
  FileOfs438,
  FileOfr439,
  FileOfs439,
  FileOfr440,
  FileOfs440,
  FileOfr441,
  FileOfs441,
  FileOfr442,
  FileOfs442,
  FileOfr443,
  FileOfs443,
  FileOfr444,
  FileOfs444,
  FileOfr445,
  FileOfs445,
  FileOfr446,
  FileOfs446,
  FileOfr447,
  FileOfs447,
  FileOfr448,
  FileOfs448,
  FileOfr449,
  FileOfs449,
  FileOfr450,
  FileOfs450,
  FileOfr451,
  FileOfs451,
  FileOfr452,
  FileOfs452,
  FileOfr453,
  FileOfs453,
  FileOfr454,
  FileOfs454,
  FileOfr455,
  FileOfs455,
  FileOfr456,
  FileOfs456,
  FileOfr457,
  FileOfs457,
  FileOfr458,
  FileOfs458,
  FileOfr459,
  FileOfs459,
  FileOfr460,
  FileOfs460,
  FileOfr461,
  FileOfs461,
  FileOfr462,
  FileOfs462,
  FileOfr463,
  FileOfs463,
  FileOfr464,
  FileOfs464,
  FileOfr465,
  FileOfs465,
  FileOfr466,
  FileOfs466,
  FileOfr467,
  FileOfs467,
  FileOfr468,
  FileOfs468,
  FileOfr469,
  FileOfs469,
  FileOfr470,
  FileOfs470,
  FileOfr471,
  FileOfs471,
  FileOfr472,
  FileOfs472,
  FileOfr473,
  FileOfs473,
  FileOfr474,
  FileOfs474,
  FileOfr475,
  FileOfs475,
  FileOfr476,
  FileOfs476,
  FileOfr477,
  FileOfs477,
  FileOfr478,
  FileOfs478,
  FileOfr479,
  FileOfs479,
  FileOfr480,
  FileOfs480,
  FileOfr481,
  FileOfs481,
  FileOfr482,
  FileOfs482,
  FileOfr483,
  FileOfs483,
  FileOfr484,
  FileOfs484,
  FileOfr485,
  FileOfs485,
  FileOfr486,
  FileOfs486,
  FileOfr487,
  FileOfs487,
  FileOfr488,
  FileOfs488,
  FileOfr489,
  FileOfs489,
  FileOfr490,
  FileOfs490,
  FileOfr491,
  FileOfs491,
  FileOfr492,
  FileOfs492,
  FileOfr493,
  FileOfs493,
  FileOfr494,
  FileOfs494,
  FileOfr495,
  FileOfs495,
  FileOfr496,
  FileOfs496,
  FileOfr497,
  FileOfs497,
  FileOfr498,
  FileOfs498,
  FileOfr499,
  FileOfs499,
  FileOfr500,
  FileOfs500
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SecurityEvent {
  id: string;
  type: 'threat' | 'vulnerability' | 'breach' | 'anomaly' | 'scan' | 'block';
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: Date;
  source: string;
  destination?: string;
  status: 'active' | 'resolved' | 'investigating' | 'false_positive';
  affectedSystems: string[];
  remediation?: string;
  mitigation?: string;
  impact: string;
  confidence: number;
  category: string;
  subcategory: string;
  tags: string[];
  metadata: Record<string, any>;
}

interface SecurityMetric {
  name: string;
  value: number;
  threshold: number;
  status: 'good' | 'warning' | 'critical';
  trend: number;
  icon: React.ComponentType<any>;
  unit: string;
  description: string;
  category: string;
  history: number[];
}

interface SecurityRule {
  id: string;
  name: string;
  description: string;
  type: 'firewall' | 'intrusion' | 'malware' | 'phishing' | 'data_loss' | 'access_control';
  enabled: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
  action: 'allow' | 'deny' | 'log' | 'alert' | 'quarantine';
  conditions: {
    field: string;
    operator: string;
    value: string | number;
  }[];
  exceptions: string[];
  schedule?: {
    start: string;
    end: string;
    days: string[];
  };
  lastTriggered?: Date;
  triggerCount: number;
  falsePositiveRate: number;
  effectiveness: number;
  category: string;
  tags: string[];
}

interface SecurityAsset {
  id: string;
  name: string;
  type: 'server' | 'workstation' | 'mobile' | 'iot' | 'network' | 'storage' | 'application';
  status: 'secure' | 'vulnerable' | 'compromised' | 'offline' | 'maintenance';
  riskScore: number;
  lastScan: Date;
  vulnerabilities: number;
  patches: number;
  location: string;
  owner: string;
  criticality: 'low' | 'medium' | 'high' | 'critical';
  compliance: number;
  dataClassification: 'public' | 'internal' | 'confidential' | 'restricted';
  securityControls: string[];
  threats: string[];
  metadata: Record<string, any>;
}

export const SecurityDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isRealtime, setIsRealtime] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  const [securityEvents, setSecurityEvents] = useState<SecurityEvent[]>([]);
  const [securityMetrics, setSecurityMetrics] = useState<SecurityMetric[]>([]);
  const [securityRules, setSecurityRules] = useState<SecurityRule[]>([]);
  const [securityAssets, setSecurityAssets] = useState<SecurityAsset[]>([]);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'events', label: 'Security Events', icon: AlertTriangle },
    { id: 'metrics', label: 'Metrics', icon: BarChart3 },
    { id: 'rules', label: 'Security Rules', icon: Lock },
    { id: 'assets', label: 'Assets', icon: Server },
    { id: 'scans', label: 'Scans', icon: Scan },
    { id: 'compliance', label: 'Compliance', icon: FileCheck },
    { id: 'threats', label: 'Threat Intelligence', icon: Eye }
  ];

  const timeRanges = [
    { value: '1h', label: 'Last Hour' },
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  const severityLevels = [
    { value: 'all', label: 'All Severities', color: 'from-gray-500 to-gray-400' },
    { value: 'critical', label: 'Critical', color: 'from-red-500 to-red-400' },
    { value: 'high', label: 'High', color: 'from-orange-500 to-orange-400' },
    { value: 'medium', label: 'Medium', color: 'from-yellow-500 to-yellow-400' },
    { value: 'low', label: 'Low', color: 'from-green-500 to-green-400' }
  ];

  const eventTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'threat', label: 'Threat' },
    { value: 'vulnerability', label: 'Vulnerability' },
    { value: 'breach', label: 'Breach' },
    { value: 'anomaly', label: 'Anomaly' },
    { value: 'scan', label: 'Scan' },
    { value: 'block', label: 'Block' }
  ];

  useEffect(() => {
    // Generate mock security data
    const generateSecurityEvents = (): SecurityEvent[] => {
      const events: SecurityEvent[] = [];
      const types: SecurityEvent['type'][] = ['threat', 'vulnerability', 'breach', 'anomaly', 'scan', 'block'];
      const severities: SecurityEvent['severity'][] = ['low', 'medium', 'high', 'critical'];
      const statuses: SecurityEvent['status'][] = ['active', 'resolved', 'investigating', 'false_positive'];
      
      for (let i = 0; i < 50; i++) {
        events.push({
          id: `evt-${Date.now()}-${i}`,
          type: types[Math.floor(Math.random() * types.length)],
          severity: severities[Math.floor(Math.random() * severities.length)],
          title: `Security Event ${i + 1}`,
          description: `Detected suspicious activity from unknown source`,
          timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
          source: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
          destination: `10.0.0.${Math.floor(Math.random() * 254) + 1}`,
          status: statuses[Math.floor(Math.random() * statuses.length)],
          affectedSystems: [`Server-${Math.floor(Math.random() * 10) + 1}`],
          remediation: 'Apply security patches and update firewall rules',
          mitigation: 'Block IP address and isolate affected systems',
          impact: 'Potential data breach and system compromise',
          confidence: Math.random() * 100,
          category: 'Network Security',
          subcategory: 'Intrusion Detection',
          tags: ['network', 'intrusion', 'malware'],
          metadata: {
            protocol: 'TCP',
            port: Math.floor(Math.random() * 65535) + 1,
            payload: 'Suspicious pattern detected'
          }
        });
      }
      
      return events.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
    };

    const generateSecurityMetrics = (): SecurityMetric[] => {
      return [
        {
          name: 'Threat Detection Rate',
          value: 87.5,
          threshold: 80,
          status: 'good',
          trend: 5.2,
          icon: Shield,
          unit: '%',
          description: 'Percentage of threats successfully detected',
          category: 'Detection',
          history: [75, 78, 82, 85, 87.5]
        },
        {
          name: 'False Positive Rate',
          value: 3.2,
          threshold: 5,
          status: 'good',
          trend: -0.8,
          icon: XCircle,
          unit: '%',
          description: 'Percentage of false positive alerts',
          category: 'Accuracy',
          history: [5.5, 4.8, 4.2, 3.5, 3.2]
        },
        {
          name: 'Response Time',
          value: 45,
          threshold: 60,
          status: 'good',
          trend: -8.3,
          icon: Timer,
          unit: 'seconds',
          description: 'Average time to respond to security events',
          category: 'Response',
          history: [65, 58, 52, 48, 45]
        },
        {
          name: 'Vulnerability Coverage',
          value: 92.8,
          threshold: 90,
          status: 'good',
          trend: 2.1,
          icon: Shield,
          unit: '%',
          description: 'Percentage of known vulnerabilities covered',
          category: 'Coverage',
          history: [88, 89.5, 91, 91.8, 92.8]
        },
        {
          name: 'Security Score',
          value: 94.2,
          threshold: 85,
          status: 'good',
          trend: 1.5,
          icon: Award,
          unit: 'points',
          description: 'Overall security posture score',
          category: 'Overall',
          history: [89, 91, 92.5, 93.2, 94.2]
        },
        {
          name: 'Compliance Rate',
          value: 96.5,
          threshold: 95,
          status: 'good',
          trend: 0.8,
          icon: FileCheck,
          unit: '%',
          description: 'Compliance with security standards',
          category: 'Compliance',
          history: [94, 95, 95.5, 96, 96.5]
        }
      ];
    };

    const generateSecurityRules = (): SecurityRule[] => {
      return [
        {
          id: 'rule-001',
          name: 'Block Malicious IPs',
          description: 'Block traffic from known malicious IP addresses',
          type: 'firewall',
          enabled: true,
          severity: 'high',
          action: 'deny',
          conditions: [
            { field: 'source_ip', operator: 'in', value: 'malicious_ips' }
          ],
          exceptions: ['internal_whitelist'],
          schedule: {
            start: '00:00',
            end: '23:59',
            days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
          },
          lastTriggered: new Date(Date.now() - 3600000),
          triggerCount: 127,
          falsePositiveRate: 0.5,
          effectiveness: 98.5,
          category: 'Network Security',
          tags: ['firewall', 'ip_blocking', 'malicious']
        },
        {
          id: 'rule-002',
          name: 'Detect SQL Injection',
          description: 'Detect and block SQL injection attempts',
          type: 'intrusion',
          enabled: true,
          severity: 'critical',
          action: 'alert',
          conditions: [
            { field: 'request_body', operator: 'contains', value: 'UNION SELECT' },
            { field: 'request_body', operator: 'contains', value: 'DROP TABLE' }
          ],
          exceptions: ['admin_tools'],
          triggerCount: 23,
          falsePositiveRate: 2.1,
          effectiveness: 95.2,
          category: 'Application Security',
          tags: ['sql_injection', 'web_security', 'intrusion']
        },
        {
          id: 'rule-003',
          name: 'Malware Detection',
          description: 'Detect malware in file uploads and downloads',
          type: 'malware',
          enabled: true,
          severity: 'high',
          action: 'quarantine',
          conditions: [
            { field: 'file_hash', operator: 'in', value: 'malware_signatures' }
          ],
          exceptions: ['trusted_sources'],
          triggerCount: 45,
          falsePositiveRate: 1.2,
          effectiveness: 97.8,
          category: 'Malware Protection',
          tags: ['malware', 'antivirus', 'quarantine']
        }
      ];
    };

    const generateSecurityAssets = (): SecurityAsset[] => {
      return [
        {
          id: 'asset-001',
          name: 'Web Server 01',
          type: 'server',
          status: 'secure',
          riskScore: 15,
          lastScan: new Date(Date.now() - 3600000),
          vulnerabilities: 2,
          patches: 18,
          location: 'Data Center A',
          owner: 'IT Department',
          criticality: 'high',
          compliance: 98,
          dataClassification: 'confidential',
          securityControls: ['firewall', 'antivirus', 'intrusion_detection'],
          threats: ['sql_injection', 'ddos', 'malware'],
          metadata: {
            os: 'Ubuntu 20.04',
            ip: '192.168.1.100',
            services: ['apache', 'mysql', 'ssh']
          }
        },
        {
          id: 'asset-002',
          name: 'Database Server',
          type: 'server',
          status: 'vulnerable',
          riskScore: 45,
          lastScan: new Date(Date.now() - 7200000),
          vulnerabilities: 8,
          patches: 12,
          location: 'Data Center B',
          owner: 'Database Team',
          criticality: 'critical',
          compliance: 85,
          dataClassification: 'restricted',
          securityControls: ['firewall', 'encryption', 'access_control'],
          threats: ['unauthorized_access', 'data_exfiltration', 'ransomware'],
          metadata: {
            os: 'Windows Server 2019',
            ip: '192.168.1.200',
            services: ['sql_server', 'backup_service']
          }
        },
        {
          id: 'asset-003',
          name: 'Employee Laptop',
          type: 'mobile',
          status: 'secure',
          riskScore: 25,
          lastScan: new Date(Date.now() - 1800000),
          vulnerabilities: 1,
          patches: 8,
          location: 'Remote',
          owner: 'John Doe',
          criticality: 'medium',
          compliance: 92,
          dataClassification: 'internal',
          securityControls: ['antivirus', 'vpn', 'disk_encryption'],
          threats: ['malware', 'phishing', 'theft'],
          metadata: {
            os: 'Windows 11',
            ip: '10.0.0.50',
            services: ['vpn_client', 'antivirus']
          }
        }
      ];
    };

    setSecurityEvents(generateSecurityEvents());
    setSecurityMetrics(generateSecurityMetrics());
    setSecurityRules(generateSecurityRules());
    setSecurityAssets(generateSecurityAssets());
  }, [timeRange]);

  useEffect(() => {
    if (isRealtime) {
      const interval = setInterval(() => {
        // Add new security event
        const newEvent: SecurityEvent = {
          id: `evt-${Date.now()}`,
          type: 'threat',
          severity: 'medium',
          title: 'New Security Threat Detected',
          description: 'Suspicious activity detected from unknown source',
          timestamp: new Date(),
          source: `192.168.1.${Math.floor(Math.random() * 254) + 1}`,
          status: 'active',
          affectedSystems: [`Server-${Math.floor(Math.random() * 10) + 1}`],
          confidence: Math.random() * 100,
          category: 'Network Security',
          subcategory: 'Intrusion Detection',
          tags: ['network', 'intrusion'],
          metadata: {
            protocol: 'TCP',
            port: Math.floor(Math.random() * 65535) + 1
          }
        };

        setSecurityEvents(prev => [newEvent, ...prev.slice(0, 49)]);
      }, 10000);

      return () => clearInterval(interval);
    }
  }, [isRealtime]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400 bg-red-500/20';
      case 'high': return 'text-orange-400 bg-orange-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'low': return 'text-green-400 bg-green-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'secure': return 'text-green-400';
      case 'vulnerable': return 'text-yellow-400';
      case 'compromised': return 'text-red-400';
      case 'offline': return 'text-gray-400';
      case 'maintenance': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const filteredEvents = securityEvents.filter(event => {
    const matchesSeverity = filterSeverity === 'all' || event.severity === filterSeverity;
    const matchesType = filterType === 'all' || event.type === filterType;
    const matchesSearch = searchQuery === '' || 
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      event.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSeverity && matchesType && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-red-400 to-orange-600 bg-clip-text text-transparent mb-2">
              Security Dashboard
            </h1>
            <p className="text-gray-400">
              Real-time security monitoring and threat detection
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Time Range Selector */}
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            >
              {timeRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>

            {/* Realtime Toggle */}
            <motion.button
              onClick={() => setIsRealtime(!isRealtime)}
              className={cn(
                'px-4 py-2 rounded-lg transition-colors',
                isRealtime ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300'
              )}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isRealtime ? 'Realtime' : 'Historical'}
            </motion.button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="flex space-x-1 mb-8 border-b border-gray-700">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center space-x-2 px-4 py-3 border-b-2 transition-colors',
              activeTab === tab.id
                ? 'border-blue-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            )}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </motion.button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {/* Security Metrics Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
              {securityMetrics.map((metric, index) => (
                <motion.div
                  key={metric.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-gray-800 border border-gray-700 rounded-xl p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <metric.icon className={cn('w-8 h-8', getStatusColor(metric.status))} />
                    <div className={cn(
                      'px-2 py-1 rounded text-xs font-medium',
                      metric.status === 'good' ? 'bg-green-500/20 text-green-400' :
                      metric.status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    )}>
                      {metric.status}
                    </div>
                  </div>
                  
                  <div className="text-2xl font-bold mb-2">
                    {metric.value}{metric.unit}
                  </div>
                  <div className="text-sm text-gray-400 mb-3">{metric.name}</div>
                  
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">{metric.description}</span>
                    <div className="flex items-center space-x-1">
                      {metric.trend > 0 ? (
                        <TrendingUp className="w-3 h-3 text-green-400" />
                      ) : (
                        <TrendingDown className="w-3 h-3 text-red-400" />
                      )}
                      <span className={metric.trend > 0 ? 'text-green-400' : 'text-red-400'}>
                        {Math.abs(metric.trend)}%
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Recent Security Events */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-white">Recent Security Events</h3>
                <button className="text-blue-400 hover:text-blue-300 text-sm">
                  View All Events
                </button>
              </div>
              
              <div className="space-y-3">
                {filteredEvents.slice(0, 5).map((event) => (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center justify-between p-4 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors cursor-pointer"
                    onClick={() => setSelectedEvent(event)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={cn(
                        'w-3 h-3 rounded-full',
                        event.severity === 'critical' ? 'bg-red-400' :
                        event.severity === 'high' ? 'bg-orange-400' :
                        event.severity === 'medium' ? 'bg-yellow-400' :
                        'bg-green-400'
                      )} />
                      <div>
                        <div className="font-medium text-white">{event.title}</div>
                        <div className="text-sm text-gray-400">{event.description}</div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <span className={cn(
                        'px-2 py-1 rounded text-xs font-medium',
                        getSeverityColor(event.severity)
                      )}>
                        {event.severity}
                      </span>
                      <span className="text-sm text-gray-400">
                        {event.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'events' && (
          <motion.div
            key="events"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {/* Filters */}
            <div className="flex items-center space-x-4 mb-6">
              <input
                type="text"
                placeholder="Search events..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              />
              
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              >
                {severityLevels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
              
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 focus:outline-none"
              >
                {eventTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Events List */}
            <div className="space-y-3">
              {filteredEvents.map((event) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-gray-800 border border-gray-700 rounded-xl p-6 hover:border-blue-500 transition-colors cursor-pointer"
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={cn(
                        'w-4 h-4 rounded-full',
                        event.severity === 'critical' ? 'bg-red-400' :
                        event.severity === 'high' ? 'bg-orange-400' :
                        event.severity === 'medium' ? 'bg-yellow-400' :
                        'bg-green-400'
                      )} />
                      <div>
                        <h4 className="font-semibold text-white">{event.title}</h4>
                        <p className="text-sm text-gray-400">{event.description}</p>
                        <div className="flex items-center space-x-4 mt-2">
                          <span className="text-xs text-gray-500">
                            Source: {event.source}
                          </span>
                          {event.destination && (
                            <span className="text-xs text-gray-500">
                              Destination: {event.destination}
                            </span>
                          )}
                          <span className="text-xs text-gray-500">
                            {event.timestamp.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <span className={cn(
                        'px-3 py-1 rounded text-xs font-medium',
                        getSeverityColor(event.severity)
                      )}>
                        {event.severity}
                      </span>
                      <span className={cn(
                        'px-3 py-1 rounded text-xs font-medium',
                        event.status === 'active' ? 'bg-blue-500/20 text-blue-400' :
                        event.status === 'resolved' ? 'bg-green-500/20 text-green-400' :
                        event.status === 'investigating' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-gray-500/20 text-gray-400'
                      )}>
                        {event.status}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Event Details Modal */}
      <AnimatePresence>
        {selectedEvent && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-6"
            onClick={() => setSelectedEvent(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-800 rounded-xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">{selectedEvent.title}</h2>
                <motion.button
                  onClick={() => setSelectedEvent(null)}
                  className="p-2 hover:bg-gray-700 rounded-lg"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X className="w-5 h-5" />
                </motion.button>
              </div>

              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-2">Event Details</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-400">Type</span>
                      <p className="text-white">{selectedEvent.type}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-400">Severity</span>
                      <p className={cn('capitalize', getSeverityColor(selectedEvent.severity))}>
                        {selectedEvent.severity}
                      </p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-400">Status</span>
                      <p className="capitalize text-white">{selectedEvent.status}</p>
                    </div>
                    <div>
                      <span className="text-sm text-gray-400">Confidence</span>
                      <p className="text-white">{selectedEvent.confidence.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">Description</h3>
                  <p className="text-gray-300">{selectedEvent.description}</p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">Network Information</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-gray-400">Source</span>
                      <p className="text-white">{selectedEvent.source}</p>
                    </div>
                    {selectedEvent.destination && (
                      <div>
                        <span className="text-sm text-gray-400">Destination</span>
                        <p className="text-white">{selectedEvent.destination}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">Impact & Response</h3>
                  <div className="space-y-3">
                    <div>
                      <span className="text-sm text-gray-400">Impact</span>
                      <p className="text-gray-300">{selectedEvent.impact}</p>
                    </div>
                    {selectedEvent.remediation && (
                      <div>
                        <span className="text-sm text-gray-400">Remediation</span>
                        <p className="text-gray-300">{selectedEvent.remediation}</p>
                      </div>
                    )}
                    {selectedEvent.mitigation && (
                      <div>
                        <span className="text-sm text-gray-400">Mitigation</span>
                        <p className="text-gray-300">{selectedEvent.mitigation}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">Affected Systems</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedEvent.affectedSystems.map((system) => (
                      <span key={system} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">
                        {system}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-2">Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {selectedEvent.tags.map((tag) => (
                      <span key={tag} className="px-3 py-1 bg-gray-700 text-gray-300 rounded text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SecurityDashboard;
