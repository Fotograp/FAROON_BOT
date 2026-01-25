import React from 'react';
import { FiMapPin, FiNavigation, FiDownload, FiHeart, FiShare2, FiChevronLeft } from 'react-icons/fi';
import './LocationScreen.css';

const LocationScreen = ({ location, onBack }) => {
  const currentLocation = {
    name: 'Пик Большой Борус',
    location: 'Красноярский край, Шушенский район',
    image: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80',
    difficulty: 'Средняя',
    duration: '10-12 часов',
    distance: '18 км',
    elevation: '1200 м',
    description: 'Высочайшая вершина хребта Борус (2318 м) в Западном Саяне. Расположен в национальном парке "Шушенский бор". Маршрут проходит через кедровую тайгу, альпийские луга и горную тундру. С вершины открывается панорама на Саянские хребты и долину Енисея.',
    landscape: 'Кедровая тайга сменяется субальпийскими лугами, затем горной тундрой с каменными россыпями. Финальный подъём по скальным участкам. Вершина представляет собой скальный гребень.',
    tips: 'Старт в 6:00-7:00 для завершения до темноты. Последний источник воды на 5 км от начала. Запас воды 3+ литра обязателен. Погода в горах непредсказуема - возможны внезапные туманы и похолодания.'
  };

  return (
    <div className="app-container">
      <div className="location-nav">
        <button className="nav-btn" onClick={onBack}>
          <FiChevronLeft size={20} />
        </button>
        <div className="nav-actions">
          <button className="nav-btn"><FiShare2 size={18} /></button>
          <button className="nav-btn"><FiHeart size={18} /></button>
        </div>
      </div>

      <img src={currentLocation.image} alt={currentLocation.name} className="location-image" />

      <div className="location-content">
        <h1 className="location-title">{currentLocation.name}</h1>
        <p className="location-subtitle"><FiMapPin /> {currentLocation.location}</p>

        <div className="location-stats">
          <div className="stat-card"><div className="stat-value">{currentLocation.difficulty}</div><div className="stat-label">Сложность</div></div>
          <div className="stat-card"><div className="stat-value">{currentLocation.duration}</div><div className="stat-label">Время</div></div>
          <div className="stat-card"><div className="stat-value">{currentLocation.distance}</div><div className="stat-label">Дистанция</div></div>
          <div className="stat-card"><div className="stat-value">{currentLocation.elevation}</div><div className="stat-label">Набор высоты</div></div>
        </div>

        <div className="info-section">
          <h3 className="section-title">ОПИСАНИЕ МАРШРУТА</h3>
          <p className="section-text">{currentLocation.description}</p>
        </div>
        <div className="info-section">
          <h3 className="section-title">ОСОБЕННОСТИ ЛАНДШАФТА</h3>
          <p className="section-text">{currentLocation.landscape}</p>
        </div>
        <div className="info-section">
          <h3 className="section-title">РЕКОМЕНДАЦИИ И СОВЕТЫ</h3>
          <p className="section-text">{currentLocation.tips}</p>
        </div>
      </div>

      <div className="quick-actions">
        <button className="action-btn"><FiNavigation /> Навигация</button>
        <button className="action-btn"><FiDownload /> Скачать</button>
        <button className="action-btn"><FiHeart /> В избранное</button>
      </div>
    </div>
  );
};

export default LocationScreen;
