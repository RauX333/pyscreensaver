CREATE TABLE IF NOT EXISTS "frame" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "createdAt" TEXT NOT NULL, "imageFileName" TEXT NOT NULL, "segmentId" INTEGER REFERENCES "segment" ("id"), "videoId" INTEGER REFERENCES "video" ("id"), "videoFrameIndex" INTEGER, "isStarred" INTEGER NOT NULL DEFAULT (0), "encodingStatus" TEXT);

CREATE TABLE IF NOT EXISTS "segment" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "appId" TEXT, "startTime" TEXT NOT NULL, "endTime" TEXT NOT NULL, "windowName" TEXT, "browserUrl" TEXT, "path" TEXT);

CREATE TABLE IF NOT EXISTS "video" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "frameDuration" REAL NOT NULL, "height" INTEGER NOT NULL, "width" INTEGER NOT NULL, "path" TEXT NOT NULL DEFAULT (''), "captureType" TEXT, "fileSize" INTEGER);

CREATE INDEX "index_frame_on_segmentid_createdat" ON "frame" ("segmentId", "createdAt");

CREATE INDEX "index_frame_on_createdat" ON "frame" ("createdAt");

CREATE TABLE IF NOT EXISTS 'search_content'(docid INTEGER PRIMARY KEY, 'c0text', 'c1otherText');

CREATE INDEX "index_frame_on_isstarred_createdat" ON "frame" ("isStarred", "createdAt");

CREATE INDEX "index_frame_on_videoid" ON "frame" ("videoId");

CREATE INDEX "index_segment_on_starttime" ON "segment" ("startTime");

CREATE TABLE IF NOT EXISTS "doc_segment" ("docid" INTEGER NOT NULL UNIQUE REFERENCES "search" ("docid"), "segmentId" INTEGER NOT NULL REFERENCES "segment" ("id"), "frameId" INTEGER REFERENCES "frame" ("id"));

CREATE INDEX "index_doc_segment_on_segmentid_docid" ON "doc_segment" ("segmentId", "docid");

CREATE INDEX "index_doc_segment_on_frameid_docid" ON "doc_segment" ("frameId", "docid");

CREATE TABLE IF NOT EXISTS "segment_video" ("segmentId" INTEGER NOT NULL REFERENCES "segment" ("id"), "videoId" INTEGER NOT NULL REFERENCES "video" ("id"), "startTime" TEXT NOT NULL, "endTime" TEXT NOT NULL);

CREATE INDEX "index_segment_video_on_segmentid_starttime_endtime" ON "segment_video" ("segmentId", "startTime", "endTime");

CREATE INDEX "index_segment_on_appid" ON "segment" ("appId");