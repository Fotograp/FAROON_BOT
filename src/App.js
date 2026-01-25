import React from 'react';
import './styles/globals.css';
import LocationScreen from './screens/LocationScreen';

function App() {
  // Пока что просто показываем карточку локации
  // Позже добавим навигацию между экранами
  return (
    <LocationScreen 
      location={null} // Данные уже внутри компонента
      onBack={() => console.log('Назад')} // Заглушка
    />
  );
}

export default App;
