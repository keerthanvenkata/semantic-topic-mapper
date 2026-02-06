# Split document into coarse blocks (e.g. by paragraph / double newline).
#
# Role: ingestion only — prepare text into segments for downstream use.
# Does not detect topics or interpret structure; that belongs in structure/
# (header_detector, topic_id_parser). Rule: ingestion prepares text,
# structure interprets structure.
