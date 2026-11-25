import {
  CalendarDays,
  MapPin,
  Image,
  FileText,
  Mic,
  Heart,
  ArrowRight,
} from "lucide-react";

function TripCard({ trip }) {
  return (
    <div className="trip-card">
      {/* Cover Image */}
      <div className="trip-image">
        <img src={trip.cover} alt={trip.title} />

        <span className="trip-badge">{trip.mood}</span>
      </div>

      {/* Card Body */}
      <div className="trip-content">
        <h3>{trip.title}</h3>

        <p className="trip-description">{trip.description}</p>

        {/* Date */}
        <div className="trip-row">
          <CalendarDays size={18} />
          <span>{trip.date}</span>
        </div>

        {/* Location */}
        <div className="trip-row">
          <MapPin size={18} />
          <span>{trip.location}</span>
        </div>

        {/* Statistics */}
        <div className="trip-stats">
          <div className="stat-box">
            <Image size={18} />
            <span>{trip.photos} Photos</span>
          </div>

          <div className="stat-box">
            <FileText size={18} />
            <span>{trip.documents} Docs</span>
          </div>

          <div className="stat-box">
            <Mic size={18} />
            <span>{trip.voiceNotes} Notes</span>
          </div>
        </div>

        {/* Footer */}
        <div className="trip-footer">
          <div className="memory-score">
            <Heart size={18} />
            <span>Favorite Memory</span>
          </div>

          <button className="trip-btn">
            View Trip
            <ArrowRight size={18} />
          </button>
        </div>
      </div>
    </div>
  );
}

export default TripCard;
