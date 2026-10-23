export const HERO_SCENES=[
 {src:'/silvermoon.jpg',name:'Silvermoon City',alt:'Silvermoon’s golden spires and courtyard'},
 {src:'/heroes/eversong.webp',name:'Eversong Woods',alt:'Golden trees and elven architecture in Eversong Woods'},
 {src:'/heroes/zulaman.webp',name:'Zul’Aman',alt:'The ancient Amani homeland beneath the forests of Zul’Aman'},
 {src:'/heroes/harandar.webp',name:'Harandar',alt:'Luminous mushrooms and the primordial jungle of Harandar'},
 {src:'/heroes/voidstorm.webp',name:'Voidstorm',alt:'The otherworldly skies and landscape of the Voidstorm'}
] as const;
export type HeroScene=typeof HERO_SCENES[number];
