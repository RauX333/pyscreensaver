import sqlite3
from utils import db_ext_path, db_path
from log import log


class database:
    def __init__(self):
        dbName = db_path
        # judge if database not existed ?
        self.conn = sqlite3.connect(dbName)
        self.conn.enable_load_extension(True)
        self.conn.load_extension(str(db_ext_path))
        self.csr = self.conn.cursor()
        log.logger.info("Database %s connected/created successfully!", dbName)

    def initTable(self):

        self.csr.execute("""CREATE TABLE IF NOT EXISTS "segment" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "appId" TEXT, "startTime" TEXT NOT NULL, "endTime" TEXT NOT NULL, "windowName" TEXT, "browserUrl" TEXT, "path" TEXT)""")
        self.csr.execute("""CREATE TABLE IF NOT EXISTS "frame" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "createdAt" TEXT NOT NULL, "imageFileName" TEXT NOT NULL, "segmentId" INTEGER REFERENCES "segment" ("id"), "videoId" INTEGER REFERENCES "video" ("id"), "videoFrameIndex" INTEGER, "isStarred" INTEGER NOT NULL DEFAULT (0), "encodingStatus" TEXT, "ocrStatus" TEXT, "title" TEXT, "content" TEXT)""")
        self.csr.execute("""CREATE TABLE IF NOT EXISTS "video" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "frameDuration" REAL NOT NULL, "height" INTEGER NOT NULL, "width" INTEGER NOT NULL, "path" TEXT NOT NULL DEFAULT (''), "captureType" TEXT, "fileSize" INTEGER)""")
        self.csr.execute(
            """CREATE VIRTUAL TABLE IF NOT EXISTS frame_fts USING FTS5(title,content,content='frame', content_rowid='id',tokenize='simple')""")
        # self.csr.execute("""CREATE TABLE IF NOT EXISTS "doc_segment" ("docId" INTEGER NOT NULL UNIQUE, "segmentId" INTEGER NOT NULL REFERENCES "segment" ("id"), "frameId" INTEGER REFERENCES "frame" ("id"))""")
        self.csr.execute("""CREATE TABLE IF NOT EXISTS "segment" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "appId" TEXT, "startTime" TEXT NOT NULL, "endTime" TEXT NOT NULL, "windowName" TEXT, "browserUrl" TEXT, "path" TEXT)""")
        self.csr.execute("""CREATE TABLE IF NOT EXISTS "segment_video" ("segmentId" INTEGER NOT NULL REFERENCES "segment" ("id"), "videoId" INTEGER NOT NULL REFERENCES "video" ("id"), "startTime" TEXT NOT NULL, "endTime" TEXT NOT NULL)""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_frame_on_segmentid_createdat" ON "frame" ("segmentId", "createdAt")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_frame_on_createdat" ON "frame" ("createdAt")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_frame_on_isstarred_createdat" ON "frame" ("isStarred", "createdAt")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_frame_on_videoid" ON "frame" ("videoId")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_frame_on_ocrstatus" ON "frame" ("ocrStatus")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_segment_on_starttime" ON "segment" ("startTime")""")
        # self.csr.execute(
        #     """CREATE INDEX IF NOT EXISTS "index_doc_segment_on_segmentid_docid" ON "doc_segment" ("segmentId", "docId")""")
        # self.csr.execute(
        #     """CREATE INDEX IF NOT EXISTS "index_doc_segment_on_frameid_docid" ON "doc_segment" ("frameId", "docId")""")
        # self.csr.execute(
        #     """CREATE INDEX IF NOT EXISTS "index_doc_segment_on_docid" ON "doc_segment" ("docId")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_segment_video_on_segmentid_starttime_endtime" ON "segment_video" ("segmentId", "startTime", "endTime")""")
        self.csr.execute(
            """CREATE INDEX IF NOT EXISTS "index_segment_on_appid" ON "segment" ("appId")""")
        self.csr.executescript("""
            CREATE TRIGGER  IF NOT EXISTS frame_ai AFTER INSERT ON frame
                BEGIN
                    INSERT INTO frame_fts (rowid, title,content)
                    VALUES (new.id, new.title,new.content);
                END;

            CREATE TRIGGER  IF NOT EXISTS frame_ad AFTER DELETE ON frame
                BEGIN
                    INSERT INTO frame_fts (frame_fts, rowid, title, content)
                    VALUES ('delete', old.id, old.title, old.content);
                END;

            CREATE TRIGGER  IF NOT EXISTS frame_au AFTER UPDATE ON frame
                BEGIN
                    INSERT INTO frame_fts (frame_fts, rowid, title,content)
                    VALUES ('delete', old.id, old.title, old.content);
                    INSERT INTO frame_fts (rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;
        """)
        self.conn.commit()

    def addSegment(self, appId, startTime, endTime, windowName, browserUrl, path):
        self.csr.execute("insert into segment (appId,startTime,endTime,windowName,browserUrl,path) values (?,?,?,?,?,?) ",
                         (appId, startTime, endTime, windowName, browserUrl, path))
        id = self.csr.lastrowid
        self.conn.commit()
        return id

    def updateSegment(self, id, endTime):
        self.csr.execute(
            "update segment set endTime = ? where id = ? ", (endTime, id))
        self.conn.commit()

    def addFrame(self, createdAt, imageFileName, segmentId, encodingStatus, ocrStatus, title, content):
        self.csr.execute("insert into frame (createdAt,imageFileName,segmentId,encodingStatus,ocrStatus,title,content) values (?,?,?,?,?,?,?)",
                         (createdAt, imageFileName, segmentId, encodingStatus, ocrStatus, title, content))
        self.conn.commit()

    def findUnocredFrame(self):
        self.csr.execute(
            "select id,imageFileName from frame where ocrStatus = 0 ORDER BY createdAt LIMIT 10")
        rows = self.csr.fetchall()
        print(rows)
        return rows

    def addOcr(self, id, content):
        self.csr.execute(
            "update frame set content=?,ocrStatus = 1 where id = ?", (content, id))
        self.conn.commit()

    def failOcr(self, id):
        self.csr.execute(
            "update frame set ocrStatus = 2 where id = ?", (id,))
        self.conn.commit()

    def findOcr(self, word):
        self.csr.execute(
            "SELECT rowid,title,content FROM frame_fts where frame_fts match ? ORDER BY rank", (word,))
        rows = self.csr.fetchall()
        # for row in rows:
        #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> aaaaaa", row)
    def findUnEncodedFrames(self):
        #TODO: find frame by segementid and make sure all the frame not exceed 5mins
        self.csr.execute(
            "select id,imageFileName,segmentId from frame where encodingStatus = 0 ORDER BY createdAt LIMIT 600")
        rows = self.csr.fetchall()
        print(rows)
        return rows
    def updateEncodedFrame(self, id):
        self.csr.execute(
            "update frame set encodingStatus = 1 where id = ?", (id,))
        self.conn.commit()