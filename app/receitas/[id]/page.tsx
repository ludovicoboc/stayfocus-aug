'use client';

import { useParams } from 'next/navigation';
import { DetalhesReceita } from '../../components/receitas/DetalhesReceita';

// This page will be dynamically rendered based on the [id] parameter
export default function ReceitaDetalhesPage() {
  const params = useParams();
  const id = params?.id ? (Array.isArray(params.id) ? params.id[0] : params.id) : '';
  
  // The DetalhesReceita component handles fetching the recipe data using the id
  return <DetalhesReceita id={id} />;
}

// Optional: Add generateStaticParams if you want to pre-render some recipe pages at build time
// export async function generateStaticParams() {
//   // Fetch a list of recipe IDs from your data source (e.g., the store or an API)
//   // const recipes = await fetchRecipes(); // Replace with your data fetching logic
//   // return recipes.map((recipe) => ({
//   //   id: recipe.id,
//   // }));
//   return []; // Return empty array if not pre-rendering
// }
